import asyncio 
import aiohttp
from .models import _ASROptions, STTEncoding, STTModels, STTLanguages
from .log import logger 
from livekit.agents.stt.stream_adapter import StreamAdapter
from livekit.agents import stt
from livekit.agents import vad

class CustomStreamAdapter(StreamAdapter):
    def __init__(self, stt, vad):
        super().__init__(stt=stt, vad=vad)
        self._buffer = asyncio.Queue()
        self._is_running = True
        self.stt_engine = stt
        self.vad_engine = vad
    
    def __aiter__(self):
        return self
        
    async def __anext__(self):
        if not self._is_running:
            raise StopAsyncIteration
        
        try:
            item = await self._buffer.get()
            if item is None: 
                self._is_running = False
                raise StopAsyncIteration
            return item
        except Exception as e:
            logger.error(f"Error in __anext__: {e}")
            self._is_running = False
            raise StopAsyncIteration
    
    def push_frame(self, frame):
        """
        Receives audio frames and processes them through the STT pipeline
        """
        try:
            if hasattr(super(), 'push_frame'):
                super().push_frame(frame)
            else:
                asyncio.create_task(self._process_frame(frame))
        except Exception as e:
            logger.error(f"Error in push_frame: {e}")
    
    async def _process_frame(self, frame):
        """
        Process an audio frame through the VAD and STT pipeline
        """
        is_voice = await self.vad_engine.detect(frame)
        
        if is_voice:
            try:
                audio_iter = [frame] 
                async for result in self.stt_engine._recognize_impl(self._frame_iterator(audio_iter)):
                    await self._buffer.put(result)
            except Exception as e:
                logger.error(f"Error processing frame through STT: {e}")
    
    async def _frame_iterator(self, frames):
        """Helper to convert a list of frames into an async iterator"""
        for frame in frames:
            yield frame
    
    def close(self):
        """Signal that we're done with the stream"""
        asyncio.create_task(self._buffer.put(None))  
        self._is_running = False

class WhisperASR(stt.STT):  
    def __init__(
        self,
        *,
        endpoint: str,
        sample_rate: int = 16000,
        model: STTModels = "whisper",
        language: STTLanguages = "en",
        encoding: STTEncoding = "pcm_s16le"
    ) -> None:
        """
        Whisper KIPPS STT
        """
        super().__init__(
             capabilities=stt.STTCapabilities(streaming=True, interim_results=False),
        )
        self.opts = _ASROptions(
            model=model,
            encoding=encoding,
            sample_rate=sample_rate,
            languages=language,
            endpoint=endpoint,
        )

    async def _recognize_impl(self, audio_iter):
        """
        Implements the abstract method required by the base class.
        Simply wraps the transcribe method.
        """
        async for result in self.transcribe(audio_iter):
            yield result

    async def transcribe(self, audio_iter):
        async with aiohttp.ClientSession() as session:
            ws_url = f"{self.opts.endpoint}/listen"
            async with session.ws_connect(ws_url) as ws:
                sender_task = asyncio.create_task(self._sender(ws, audio_iter))
                async for msg in ws:
                    if msg.type == aiohttp.WSMsgType.TEXT:
                        result = msg.json()
                        logger.info(f"Received transcription: {result}")
                        yield result
                    elif msg.type == aiohttp.WSMsgType.ERROR:
                        logger.error("WebSocket encountered an error.")
                        break
                await sender_task

    async def _sender(self, ws, audio_iter):
        async for audio in audio_iter:
            await ws.send_bytes(audio)
        await ws.close()

    def stream(self):
        class BasicVAD(vad.VAD):
            def __init__(self):
                super().__init__(
                    capabilities=vad.VADCapabilities(update_interval=0.1)
                )
            
            async def detect(self, audio):
                return True 
                
            def stream(self):
                return self 
                
        voice_activity_detector = BasicVAD()
        return CustomStreamAdapter(stt=self, vad=voice_activity_detector)
