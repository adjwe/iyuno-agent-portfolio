# iyuno-agent-portfolio — agentic-knowledge-triage

!\[CI](https://github.com/adjwe/iyuno-agent-portfolio/actions/workflows/ci.yml/badge.svg)

채용공고의 요구사항을 **작동하는 증거**로 바꾼 과제 프로젝트. 공개 보안 개념 문서 20개를 검색해
근거와 함께 답하고, 필요하면 도구를 호출하는 에이전트이다.

## 대상 공고

* Iyuno **AI Agent Engineer** (서울 · Hybrid · Full-time, Req. JR101122, 마감 2026-09-30)
* 링크: https://iyuno.wd3.myworkdayjobs.com/careers/job/seoul/ai-agent-engineer\_jr101122
* ⚠ 링크와 마감일은 수업 자료 기준이다. 제출 전에 직접 다시 확인할 것.

## 공고 요구사항 ↔ 이 저장소의 증거

|공고 항목|구현|위치|상태|
|-|-|-|-|
|RAG 검색·응답 시스템|문서 20개 검색 + citation|`agent/retriever.py`, `agent/router.py`|구현 (TF-IDF, 임베딩 아님)|
|tool calling|계산기 · CVSS 등급 · 패치 정책|`agent/tools.py`|구현 (규칙 기반 호출)|
|다단계 workflow|CVSS → 등급 → 패치 기한|`agent/router.py`|구현|
|API·데이터 통합|JSON API `/ask`, `/feedback`, JSON 코퍼스|`agent/server.py`|부분 (외부 DB 없음)|
|평가·피드백 루프|30문항 지표 + 피드백 저장|`evaluation/`, `agent/feedback.py`|구현|
|latency·cost·reliability|지연 측정, 비용 0, 테스트 13개, CI|`evaluation/metrics.json`, `tests/`|구현|
|LLM 기반 Agent|—|—|**미구현** (다음 단계)|

## 실행

```bash
python -m venv .venv \&\& source .venv/bin/activate
pip install -r requirements.txt
python -m agent.cli "SQL 인젝션을 막으려면 어떻게 해야 해?"
python -m agent.cli "CVSS 9.1 취약점을 패치해야 하는 기한은 며칠이야?"
python -m agent.cli "이 답이 틀렸어" --rating down --correction "정답 메모"
python -m agent.server          # POST http://127.0.0.1:8000/ask
python -m unittest discover -s tests -v
python evaluation/evaluate.py   # metrics.json / results.csv / metrics.png 갱신
```

## 평가 결과 (30문항: RAG 22 · 도구 6 · 거부 2)

|지표|값|
|-|-|
|Recall@1 / Recall@3 (RAG)|1.00 / 1.00|
|답변 키워드 포함률 (RAG)|0.864|
|도구 호출 성공|6/6|
|범위 밖 질문 거부|2/2|
|평균 / p95 지연|0.89 ms / 1.43 ms|
|LLM 토큰 비용|0 (LLM 미사용)|

전체: `evaluation/metrics.json`, `evaluation/results.csv`, `evaluation/metrics.png`.

## 한계 (정직하게)

* 코퍼스와 질문을 같은 사람이 만들었고 문서가 20개라 Recall 1.00은 **일반화 성능이 아님**.
* LLM·임베딩·벡터 DB 미사용. 라우터는 정규식 기반이라 표현이 바뀌면 실패할 수 있음.
* 답변은 문장 추출식이라 q06, q10, q17에서 핵심 키워드가 빠짐.
* 거부 임계값(0.12)은 평가 전에 정했지만 거부 질문이 2개뿐이라 검증력이 약함.
* 패치 정책은 가상 예시.

## 데이터

`DATA\_SOURCES.md` 참고. 회고: `docs/REFLECTION.md`. 시연: `demo/demo\_session.txt` (영상/GIF는 직접 추가).

## 개발 방식

코드는 AI 어시스턴트(Claude)와 함께 작성했고 테스트와 평가를 실제로 실행해 결과를 기록했다.

## License

MIT

