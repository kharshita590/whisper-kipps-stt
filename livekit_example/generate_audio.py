import asyncio
import pyaudio
from threading import Thread
from livekit.plugins.whisper import WhisperASR
CHUNK = 1600  
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

def microphone_reader(queue, loop):
    p = pyaudio.PyAudio()
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    try:
        while True:
            data = stream.read(CHUNK)
            asyncio.run_coroutine_threadsafe(queue.put(data), loop)
    except Exception as e:
        print("Microphone error:", e)
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

async def audio_generator(queue):
    while True:
        data = await queue.get()
        yield data

async def test_stt():
    queue = asyncio.Queue()
    loop = asyncio.get_running_loop()
    mic_thread = Thread(target=microphone_reader, args=(queue, loop), daemon=True)
    mic_thread.start()
    stt = WhisperASR(
        endpoint="ws://localhost:3004",
        sample_rate=RATE,
        model="whisper",
        encoding="pcm_s16le"
    )
    
    print("Start speaking... (Press Ctrl+C to exit)")
    async for result in stt.transcribe(audio_generator(queue)):
        print("Transcription result:", result)

if __name__ == "__main__":
    try:
        asyncio.run(test_stt())
    except KeyboardInterrupt:
        print("Test terminated.")
