"""30개 질문으로 정량 평가. 사용: python evaluation/evaluate.py"""
import csv
import json
import statistics
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent.router import Agent  # noqa: E402


def run():
    agent = Agent()
    qs = json.loads((ROOT / "evaluation" / "questions.json").read_text(encoding="utf-8"))
    rows = []
    for q in qs:
        r = agent.ask(q["question"])
        row = {"id": q["id"], "type": q["type"], "question": q["question"],
               "route": r["route"], "tools": "+".join(r["tools"]),
               "retrieved": ",".join(r.get("retrieved", [])), "answer": r["answer"],
               "latency_ms": r["latency_ms"], "top_score": r.get("top_score", "")}
        kw_ok = q["keyword"] is None or q["keyword"].lower() in r["answer"].lower()
        row["keyword_ok"] = kw_ok
        if q["type"] == "rag":
            ret = r.get("retrieved", [])
            row["hit1"] = bool(ret) and ret[0] == q["expected_doc"]
            row["hit3"] = q["expected_doc"] in ret
            row["ok"] = row["hit1"] and kw_ok
        elif q["type"] == "tool":
            row["ok"] = q["expected_tool"] in r["tools"] and kw_ok
        else:
            row["ok"] = r["route"] == "abstain"
        rows.append(row)

    def rate(sel, key="ok"):
        sel = list(sel)
        return round(sum(1 for x in sel if x[key]) / len(sel), 3) if sel else None

    rag = [x for x in rows if x["type"] == "rag"]
    lat = sorted(x["latency_ms"] for x in rows)
    metrics = {
        "n_questions": len(rows),
        "n_rag": len(rag),
        "n_tool": sum(x["type"] == "tool" for x in rows),
        "n_abstain": sum(x["type"] == "abstain" for x in rows),
        "recall_at_1": rate(rag, "hit1"),
        "recall_at_3": rate(rag, "hit3"),
        "rag_answer_keyword_match": rate(rag, "keyword_ok"),
        "tool_success": rate(x for x in rows if x["type"] == "tool"),
        "abstain_success": rate(x for x in rows if x["type"] == "abstain"),
        "overall_ok": rate(rows),
        "latency_ms_mean": round(statistics.mean(lat), 2),
        "latency_ms_p95": lat[int(0.95 * (len(lat) - 1))],
        "llm_token_cost_usd": 0.0,
        "note": "런타임에 LLM을 쓰지 않아 faithfulness(LLM 판정)는 측정하지 않음. 답변은 검색된 문서의 문장을 그대로 인용함.",
    }
    (ROOT / "evaluation" / "metrics.json").write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2), encoding="utf-8")
    with open(ROOT / "evaluation" / "results.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(9, 3.4))
        names = ["Recall@1", "Recall@3", "Tool", "Abstain"]
        vals = [metrics["recall_at_1"], metrics["recall_at_3"], metrics["tool_success"],
                metrics["abstain_success"]]
        ax[0].bar(names, vals, color="#2563eb")
        ax[0].set_ylim(0, 1.05)
        ax[0].set_title("accuracy")
        for i, v in enumerate(vals):
            ax[0].text(i, v + 0.02, f"{v:.2f}", ha="center")
        ax[1].hist([x["latency_ms"] for x in rows], bins=10, color="#0f766e")
        ax[1].set_title("latency (ms)")
        fig.tight_layout()
        fig.savefig(ROOT / "evaluation" / "metrics.png", dpi=150)
    except ImportError:
        pass
    return metrics, rows


if __name__ == "__main__":
    m, rows = run()
    print(json.dumps(m, ensure_ascii=False, indent=2))
    for x in rows:
        if not x["ok"]:
            print("FAIL", x["id"], x["question"], "->", x["route"], x["retrieved"], x["top_score"])
