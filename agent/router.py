"""규칙 기반 라우터. 질문을 도구 호출 또는 RAG 경로로 보내고 다단계 workflow를 실행한다.
런타임에는 LLM API를 호출하지 않는다(비용 0, 재현 가능)."""
from __future__ import annotations

import re
import time

from .retriever import ABSTAIN_THRESHOLD, Retriever
from .tools import calculator, cvss_severity, policy_lookup

_SEV_WORDS = {"critical": "Critical", "치명": "Critical", "high": "High", "높음": "High",
              "medium": "Medium", "중간": "Medium", "low": "Low", "낮음": "Low"}


def _find_expression(q: str) -> str | None:
    for cand in re.findall(r"[\d\.\+\-\*/\(\)×÷\s]{3,}", q):
        cand = cand.strip()
        if re.search(r"[\d\)]\s*[\+\-\*/×÷]\s*[\d\(]", cand):
            return cand.replace("×", "*").replace("÷", "/")
    return None


class Agent:
    def __init__(self, retriever: Retriever | None = None):
        self.retriever = retriever or Retriever()

    def ask(self, question: str) -> dict:
        t0 = time.perf_counter()
        q = question.strip()
        low = q.lower()
        result = {"question": q, "route": "rag", "tools": [], "sources": [], "answer": ""}

        m_cvss = re.search(r"cvss[^0-9]*([0-9]+(?:\.[0-9])?)", low)
        wants_deadline = bool(re.search(r"패치.*(기한|며칠|sla)|기한.*패치", low))
        sev_word = next((v for k, v in _SEV_WORDS.items() if k in low), None)

        expr = None if m_cvss else _find_expression(q)
        if expr:
            result.update(route="tool", tools=["calculator"])
            val = calculator(expr)
            val = int(val) if float(val).is_integer() else round(val, 4)
            result["answer"] = f"{expr} = {val}"
        elif m_cvss or (wants_deadline and sev_word):
            result["route"] = "tool"
            if m_cvss:
                sev = cvss_severity(float(m_cvss.group(1)))
                result["tools"].append("cvss_severity")
                result["answer"] = f"CVSS {m_cvss.group(1)}점은 {sev} 등급이다."
            else:
                sev = sev_word
            if wants_deadline and sev in ("Critical", "High", "Medium", "Low"):
                days = policy_lookup(sev)
                result["tools"].append("policy_lookup")
                result["answer"] = (result["answer"] + " " if result["answer"] else "") + \
                    f"(예시 정책) {sev} 등급의 패치 기한은 {days}일이다."
        else:
            hits = self.retriever.search(q, k=3)
            result["retrieved"] = [h.doc_id for h in hits]
            if hits[0].score < ABSTAIN_THRESHOLD:
                result["route"] = "abstain"
                result["answer"] = "보유한 문서에서 근거를 찾지 못해 답변하지 않는다."
            else:
                sents = self.retriever.best_sentences(q, hits[0].doc_id)
                result["answer"] = " ".join(sents) + f" [{hits[0].doc_id}]"
                result["sources"] = [{"id": hits[0].doc_id, "title": hits[0].title,
                                      "url": hits[0].source}]
            result["top_score"] = round(hits[0].score, 4)

        result["answer"] = result["answer"].strip()
        result["latency_ms"] = round((time.perf_counter() - t0) * 1000, 2)
        return result
