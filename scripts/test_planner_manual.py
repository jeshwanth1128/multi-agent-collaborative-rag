import json

from app.agents.planner import create_plan


def main() -> None:
    question = (
        "Compare our Q3 sales from the company database "
        "against the targets defined in the strategy report."
    )

    plan = create_plan(question)

    print(
        json.dumps(
            plan.model_dump(mode="json"),
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
