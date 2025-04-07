import asyncio 
import aiohttp
from .models import _ASROptions, STTEncoding, STTModels, STTLanguages
from .log import logger 
from livekit.agents import stt
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
