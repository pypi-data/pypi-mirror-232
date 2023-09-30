import random


def get_system_content(system_description, available_strategies, available_manuals):
    new_line = "\n"
    random_strategies = new_line.join(
        [
            f"* {c.id} - {c.usage}"
            for c in random.sample(available_strategies, len(available_strategies))
        ]
    )
    random_manuals = (
        new_line.join(
            [
                f"* {c.id} - {c.usage}"
                for c in random.sample(available_manuals, len(available_manuals))
            ]
        )
        if available_manuals
        else ""
    )

    return (
        f"{system_description}\n\n"
        f"1. Establish the strategy to approach the task, it can be one of the following values:\n\n"
        f"{random_strategies}\n\n"
        f"2. Figure out and provide a list of ids of materials that are needed to execute the command.\n\n"
        f"You have access to the following materials:\n\n"
        f"{random_manuals}"
        "".strip()
    )
