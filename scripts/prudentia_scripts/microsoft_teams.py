import argparse
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
    workflow_path = os.path.join(workflow_dir, "microsoft_teams_workflow.json")

    with open(workflow_path, "w", encoding="utf-8") as workflow_file:
        json.dump(workflow, workflow_file, indent=2)
        workflow_file.write("\n")

    print(f"Wrote workflow JSON to {workflow_path}")


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Join a Microsoft Teams meeting as a guest via teams.live.com."
    )
    parser.add_argument(
        "--meeting-code",
        required=True,
        help="Teams meeting code (the ID that appears after /meet/ in the meeting URL).",
    )
    args = parser.parse_args()

    load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

    specification = """1. Go to 'https://teams.live.com/meet/<secret>meeting_code</secret>'.
    2. If a consent, cookie, or welcome dialog appears, dismiss it.
    3. If prompted to sign in, choose to join as a guest instead.
    4. If a name input appears, type 'Netgent' and continue.
    5. If any popup appears asking for microphone or camera access, dismiss or deny it.
    6. Click 'Join now' (or equivalent button) to enter the meeting.
    7. Wait for 10 seconds.
    8. Leave the meeting by clicking the hang-up or leave button."""
    parameters = {
        "meeting_code": args.meeting_code,
    }
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
