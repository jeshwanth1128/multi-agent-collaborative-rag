from langchain_openai import ChatOpenAI

from app.config import get_settings


def main() -> None:
    settings = get_settings()

    model = ChatOpenAI(
        model=settings.openai_model,
        api_key=settings.openai_api_key,
    )

    response = model.invoke(
        "Reply with exactly these two words: CONNECTION OK"
    )

    print(response.content)


if __name__ == "__main__":
    main()
