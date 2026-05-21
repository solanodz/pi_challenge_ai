from pathlib import Path


def load_answer_prompt(prompts_dir: Path) -> tuple[str, str]:
    raw = (prompts_dir / "answer.txt").read_text(encoding="utf-8")
    if "---SYSTEM---" not in raw or "---USER---" not in raw:
        raise ValueError("answer.txt must contain ---SYSTEM--- and ---USER--- sections")
    _, system_part = raw.split("---SYSTEM---", 1)
    system_text, user_template = system_part.split("---USER---", 1)
    return system_text.strip(), user_template.strip()
