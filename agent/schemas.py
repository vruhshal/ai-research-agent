"""
Structured data contracts for the agent.

Using Pydantic here does two jobs at once:
1. It gives the LLM a schema to target (we pass the JSON schema in the prompt).
2. It lets us *validate* what comes back, so "the model returned malformed JSON"
   becomes a caught, handled error instead of a silent bad output.
"""

from typing import List, Literal
from pydantic import BaseModel, Field, field_validator


class Plan(BaseModel):
    """Output of the planning step."""
    reasoning: str = Field(..., description="1-3 sentences on how to approach the question")
    sub_questions: List[str] = Field(..., min_length=1, max_length=5,
                                      description="Concrete, searchable sub-questions")
    tools_needed: List[Literal["web_search", "fetch_url"]] = Field(default_factory=list)

    @field_validator("sub_questions")
    @classmethod
    def non_empty_strings(cls, v):
        cleaned = [s.strip() for s in v if s and s.strip()]
        if not cleaned:
            raise ValueError("sub_questions must contain at least one non-empty string")
        return cleaned


class Source(BaseModel):
    title: str
    url: str
    snippet: str = Field(default="", description="Short supporting excerpt/summary, in our own words")


class FinalAnswer(BaseModel):
    """The structured output the whole pipeline is trying to produce."""
    user_question: str
    short_answer: str
    key_findings: List[str] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    confidence: Literal["low", "medium", "high"]
    limitations: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    next_steps: List[str] = Field(default_factory=list)

    @field_validator("confidence")
    @classmethod
    def confidence_must_match_sources(cls, v, info):
        # Not a hard constraint, just used downstream by the pipeline to sanity-check
        return v
