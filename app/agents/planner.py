from langchain_core.messages import HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.config import get_settings
from app.models.tasks import QueryPlan

SYSTEM_PROMPT = """
You are the planning agent in a multi-agent retrieval system.

Choose which specialist agents are needed for the user's question.

Available agents:

document:
Use for PDFs, reports, policies, manuals, DOCX files,
contracts, notes, and other internal documents.

database:
Use for structured information such as sales,
customers, products, transactions, inventory,
orders, employees, and numerical records.

web:
Use when current or external public information is needed.

Rules:
- Select only agents that are necessary.
- Multiple agents may be selected.
- Create one clear task per selected agent.
- Never create duplicate tasks for the same agent.
- Do not answer the user's question.
- Do not invent information.
- Keep reasoning_summary short.
"""


def get_planner_model():
    settings = get_settings()

    model = ChatGoogleGenerativeAI(
        model=settings.gemini_model,
        google_api_key=settings.gemini_api_key.get_secret_value(),
        timeout=20,
        max_retries=2,
    )

    return model.with_structured_output(QueryPlan)


def create_plan(question: str) -> QueryPlan:
    if not question.strip():
        raise ValueError("Question cannot be empty.")

    planner = get_planner_model()

    result = planner.invoke(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=question),
        ]
    )

    return result
