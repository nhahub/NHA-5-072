from pathlib import Path
import yaml
from config.settings import settings

PROMPTS_DIR = settings.BASE_DIR / "config" / "prompts"

def load_prompt(prompt_name: str) -> str:
    """Loads system_prompt string from YAML file in config/prompts/."""
    file_path = PROMPTS_DIR / f"{prompt_name}.yaml"
    if not file_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data.get("system_prompt", "").strip()
