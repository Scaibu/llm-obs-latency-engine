from pathlib import Path
from shared.errors.base import ValidationError
from python_shared import ValidationRules

BASE_DIR = Path(__file__).resolve().parents[3]
WORKFLOW_CONTRACT: Path = BASE_DIR / "contracts" / "workflows" / "latency_baseline_workflow.yaml"

def _extract_val(text: str, pattern: str) -> str:
    try:
        return ValidationRules.extract_pattern(text, pattern)
    except ValueError as e:
        raise ValidationError(str(e))

def load_workflow_contracts() -> dict:
    if not WORKFLOW_CONTRACT.exists():
        raise ValidationError(f"Contract file not found at {WORKFLOW_CONTRACT}")

    text = WORKFLOW_CONTRACT.read_text()
    validate_contract(text)

    return {
        "latency_baseline": {
            "workflow": "LatencyBaselineWorkflow",
            "version": int(_extract_val(text, r"^version:\s*(\d+)\s*$")),
            "cron": _extract_val(text, r"^schedule:\s*\n\s*cron:\s*\"(.*)\"\s*$"),
        }
    }

def validate_contract(text: str) -> None:
    required_fragments = [
        "workflow: LatencyBaselineWorkflow",
        'cron: "5 * * * *"',
        "activities:",
        "hourly_checkpoint:",
    ]
    for fragment in required_fragments:
        if fragment not in text:
            raise ValidationError(f"Missing required contract fragment: {fragment}")

    version = int(_extract_val(text, r"^version:\s*(\d+)\s*$"))
    if version < 1:
        raise ValidationError("Contract version must be positive integer")
