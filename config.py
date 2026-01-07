from pydantic import BaseModel, field_validator
from typing import Optional

class ContextBudget(BaseModel):
    instructions: str  # 255 chars max
    goal: str          # 1,500 chars
    memory: str        # 55 chars
    retrieval: str     # 550 chars
    tool_outputs: str  # 855 chars

    @field_validator('instructions', 'goal', 'memory', 'retrieval', 'tool_outputs')
    @classmethod
    def check_length(cls, v, info):
        limits = {
            'instructions': 255, 
            'goal': 1500, 
            'memory': 55, 
            'retrieval': 550, 
            'tool_outputs': 855
        }
        field_name = info.field_name
        if len(v) > limits[field_name]:
            raise ValueError(f"{field_name} exceeds {limits[field_name]} char limit")
        return v

# Configuration constants
CHUNK_SIZE = 500
TOP_K_RETRIEVAL = 10
EMBEDDING_MODEL = "text-embedding-3-small"