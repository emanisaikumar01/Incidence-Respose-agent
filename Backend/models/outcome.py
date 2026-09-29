from pydantic import BaseModel, Field


class OutcomeCreate(BaseModel):
    fix: str = Field(min_length=1)
    worked: bool