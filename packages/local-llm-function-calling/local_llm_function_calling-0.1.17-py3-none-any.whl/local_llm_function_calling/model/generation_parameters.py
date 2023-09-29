"""Inlcudes the common generation parameters
for huggingface and llama.cpp models"""

from dataclasses import dataclass


@dataclass
class SamplingParameters:
    """Parameters for sampling"""

    temperature: float = 1.0
    top_k: int = 0
    top_p: float = 0.0


@dataclass
class PenaltyParameters:
    """Parameters for penalties"""

    repetition_penalty: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0


@dataclass
class GenerationParameters:
    """Parameters for generation"""

    sampling: SamplingParameters = SamplingParameters()
    penalties: PenaltyParameters = PenaltyParameters()
