# 최종 회고 (1페이지)

## 구현한 것
- 문서 20개 ingest → TF-IDF(문자 2~4-gram) 검색 → 상위 문서의 핵심 문장 인용 + `[문서ID]` citation
- 규칙 기반 라우터로 tool calling 3종(계산기, CVSS 등급, 패치 정책)과 2단계 workflow(CVSS → 등급 → 패치 기한)
- 근거가 약하면 답변을 거부하는 abstain 경로
- 사용자 피드백(👍/👎/수정 답변)을 `data/feedback.jsonl`에 저장
- 30문항 평가(`evaluation/`), 단위·통합 테스트 13개, GitHub Actions CI

## 결과 (evaluation/metrics.json)
Recall@1 1.00 / Recall@3 1.00 (RAG 22문항), 도구 6/6, 거부 2/2, 답변 키워드 포함률 0.864, 평균 지연 ≈ 1 ms.

## 남은 것 / 정직한 한계
1. **평가가 낙관적이다.** 코퍼스와 질문을 같은 사람이 만들었고 문서가 20개뿐이라 Recall 1.00은 일반화 성능이 아니다.
2. **LLM과 임베딩을 쓰지 않았다.** 공고의 "LLM Agent", "vector search"에 해당하는 부분은 TF-IDF + 규칙 라우터로 대체했다. 다음 단계: 임베딩 + LLM 라우팅/생성.
3. 답변은 문장 추출식이라 질문에 정확히 맞는 문장을 못 고르는 경우가 있다(q06, q10, q17에서 키워드 누락).
4. faithfulness와 토큰 비용은 LLM이 없어 측정하지 않았다(비용 0).
5. FastAPI/Streamlit 대신 표준 라이브러리 HTTP 서버를 썼다. 시연 영상/GIF는 직접 녹화해야 한다.
6. 패치 정책은 가상 예시다.
