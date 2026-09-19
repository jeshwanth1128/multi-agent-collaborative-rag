"""Legacy command name retained; verifies the configured Gemini provider."""

from app.agents.planner import get_planner_model


def main():
    get_planner_model().invoke("Select the agent to search a document.")
    print("CONNECTION OK")


if __name__ == "__main__":
    main()
