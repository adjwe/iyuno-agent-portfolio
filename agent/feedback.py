"""사용자 피드백(좋아요/싫어요/수정 답변)을 재학습·평가용 데이터로 저장한다."""
from __future__ import annotations

import json
import time
from pathlib import Path

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "feedback.jsonl"


def save_feedback(question: str, answer: str, rating: str, correction: str = "",
                  path: Path | str = DEFAULT_PATH) -> dict:
    if rating not in ("up", "down"):
        raise ValueError("rating은 'up' 또는 'down'")
    row = {"ts": int(time.time()), "question": question, "answer": answer,
           "rating": rating, "correction": correction}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row
