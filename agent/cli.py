"""사용: python -m agent.cli "질문" [--rating up|down --correction "..."]"""
import argparse
import json

from .feedback import save_feedback
from .router import Agent


def main():
    p = argparse.ArgumentParser()
    p.add_argument("question")
    p.add_argument("--rating", choices=["up", "down"])
    p.add_argument("--correction", default="")
    p.add_argument("--json", action="store_true")
    a = p.parse_args()
    r = Agent().ask(a.question)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(f"[route={r['route']} tools={r['tools']} {r['latency_ms']}ms]")
        print(r["answer"])
    if a.rating:
        save_feedback(a.question, r["answer"], a.rating, a.correction)
        print("피드백 저장됨: data/feedback.jsonl")


if __name__ == "__main__":
    main()
