"""TF-IDF(문자 n-gram) 기반 검색기. 한국어 형태소 분석기 없이 동작한다."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

DEFAULT_CORPUS = Path(__file__).resolve().parent.parent / "data" / "corpus.json"
ABSTAIN_THRESHOLD = 0.12  # top-1 코사인 유사도가 이보다 낮으면 "근거 없음"


@dataclass
class Hit:
    doc_id: str
    title: str
    score: float
    source: str


class Retriever:
    def __init__(self, corpus_path: Path | str = DEFAULT_CORPUS):
        self.docs = json.loads(Path(corpus_path).read_text(encoding="utf-8"))
        self.vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4), sublinear_tf=True)
        self.matrix = self.vec.fit_transform([d["title"] + " " + d["text"] for d in self.docs])

    def search(self, query: str, k: int = 3) -> list[Hit]:
        q = self.vec.transform([query])
        scores = (self.matrix @ q.T).toarray().ravel()  # TF-IDF 행은 L2 정규화됨 -> 코사인
        order = np.argsort(-scores)[:k]
        return [
            Hit(self.docs[i]["id"], self.docs[i]["title"], float(scores[i]), self.docs[i]["source"])
            for i in order
        ]

    def best_sentences(self, query: str, doc_id: str, n: int = 2) -> list[str]:
        doc = next(d for d in self.docs if d["id"] == doc_id)
        sents = [s.strip() for s in re.split(r"(?<=[.!?])\s+", doc["text"]) if s.strip()]
        if len(sents) <= n:
            return sents
        scores = (self.vec.transform(sents) @ self.vec.transform([query]).T).toarray().ravel()
        idx = sorted(np.argsort(-scores)[:n])
        return [sents[i] for i in idx]
