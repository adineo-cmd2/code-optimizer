from typing import Optional

from pydantic import BaseModel, Field


class OptimizeSubmitIn(BaseModel):
    code: str
    language: str = "python"
    traffic: str = ""
    data_volume: str = ""
    input_size: str = ""


class BottleneckOut(BaseModel):
    id: int
    function: str
    root_cause: str
    predicted_ms: float
    priority: str
    snippet: str

    class Config:
        from_attributes = True


class VariantOut(BaseModel):
    id: int
    bottleneck_id: Optional[int] = None
    kind: str
    code: str
    complexity: str
    readability: int
    explanation: str

    class Config:
        from_attributes = True


class OptimizeSubmitOut(BaseModel):
    session_id: int
    hotspots: list = Field(default_factory=list)
    bottlenecks: list[BottleneckOut] = Field(default_factory=list)


class OptimizeSessionOut(BaseModel):
    session_id: int
    language: str
    bottlenecks: list[BottleneckOut] = Field(default_factory=list)
    variants: list[VariantOut] = Field(default_factory=list)


class OptimizeApplyIn(BaseModel):
    speed: int = Field(default=5, ge=0, le=10)
    memory: int = Field(default=5, ge=0, le=10)
    readability: int = Field(default=5, ge=0, le=10)


class OptimizeDiffOut(BaseModel):
    diff: str
