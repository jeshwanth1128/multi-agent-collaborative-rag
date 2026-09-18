from enum import Enum

from pydantic import BaseModel, Field


class AgentType(str, Enum):
    DOCUMENT = "document"
    DATABASE = "database"
    WEB = "web"


class AgentTask(BaseModel):
    agent: AgentType
    goal: str = Field(min_length=3)


class QueryPlan(BaseModel):
    reasoning_summary: str
    tasks: list[AgentTask] = Field(min_length=1)
