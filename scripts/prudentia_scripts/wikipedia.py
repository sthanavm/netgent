import asyncio
import json
import os
import sys

from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from main import NetGent


def _strip_artifacts(value):
    if isinstance(value, dict):
        return {
            key: _strip_artifacts(nested)
            for key, nested in value.items()
            if key not in ("screenshot", "har")
        }
    if isinstance(value, list):
        return [_strip_artifacts(nested) for nested in value]
    return value


def _write_workflow_artifact(generated: dict) -> None:
    workflow = generated.get("workflow")
    if not isinstance(workflow, dict):
        return

    workflow_dir = os.path.join(os.path.dirname(__file__), "..", "prudentia_workflows")
    os.makedirs(workflow_dir, exist_ok=True)
    workflow_path = os.path.join(workflow_dir, "wikipedia_workflow.json")

    with open(workflow_path, "w", encoding="utf-8") as workflow_file:
        json.dump(workflow, workflow_file, indent=2)
        workflow_file.write("\n")

    print(f"Wrote workflow JSON to {workflow_path}")


async def main() -> None:
    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

    specification = """1. Go to 'https://www.wikipedia.org'.
    2. Click the English option to enter the English version of Wikipedia.
    3. Click the menu button (3 horizontal lines) in the top left corner.
    4. Click 'Random article' from the menu.
    5. Wait for the random article page to finish loading, then stop."""
    parameters = {}
    client = NetGent(cdp_url=None, headless=False)
    generated = await client.generate(
        type="browser",
        spec=specification,
        parameters=parameters,
    )
    _write_workflow_artifact(generated)
    print(json.dumps(_strip_artifacts(generated), indent=2, default=str))


if __name__ == "__main__":
    asyncio.run(main())
