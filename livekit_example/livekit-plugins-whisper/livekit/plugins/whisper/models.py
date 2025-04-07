from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

STTEncoding=Literal["pcm_s16le"]
STTModels = Literal["whisper"]
STTLanguages=Literal["en","hi"]

@dataclass
class _ASROptions:
    model:STTModels
    encoding:STTEncoding
    sample_rate:int
    languages:STTLanguages
    endpoint:str