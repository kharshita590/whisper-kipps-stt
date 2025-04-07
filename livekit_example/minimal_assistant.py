import logging
from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, silero, deepgram
from livekit.plugins.whisper import WhisperASR
load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")
def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()
async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text="You are a voice assistant created by kipps. Your interface with users will be voice and your task is to be a helpful assistant.",
    )
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")
    whisper_stt = WhisperASR(
        endpoint="ws://localhost:3004", 
        sample_rate=16000,
        model="whisper",
        encoding="pcm_s16le"
    )
    deepgram_tts = deepgram.TTS()
    assistant = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=whisper_stt,
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=deepgram_tts,  
        chat_ctx=initial_ctx,
    )
    assistant.start(ctx.room, participant)
    await assistant.say("Hey, how can I help you today?", allow_interruptions=True)
if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
