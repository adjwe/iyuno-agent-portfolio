import json
import tempfile
import threading
import unittest
import urllib.request
from pathlib import Path

from agent.feedback import save_feedback
from agent.retriever import Retriever
from agent.router import Agent
from agent.server import make_server


class AgentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.agent = Agent(Retriever())

    def test_corpus_has_20_docs(self):
        self.assertEqual(len(self.agent.retriever.docs), 20)

    def test_rag_cites_source(self):
        r = self.agent.ask("SQL 인젝션을 막으려면 어떻게 해야 해?")
        self.assertEqual(r["route"], "rag")
        self.assertEqual(r["sources"][0]["id"], "owasp-a03")
        self.assertIn("[owasp-a03]", r["answer"])

    def test_multi_step_tool_workflow(self):
        r = self.agent.ask("CVSS 9.1 취약점을 패치해야 하는 기한은 며칠이야?")
        self.assertEqual(r["tools"], ["cvss_severity", "policy_lookup"])
        self.assertIn("3일", r["answer"])

    def test_calculator_route(self):
        r = self.agent.ask("12.5 * 8 계산해줘")
        self.assertEqual(r["tools"], ["calculator"])
        self.assertIn("100", r["answer"])

    def test_sha1_is_not_math(self):
        r = self.agent.ask("MD5나 SHA-1 같은 오래된 해시를 쓰면 왜 문제야?")
        self.assertEqual(r["route"], "rag")

    def test_abstain_out_of_scope(self):
        self.assertEqual(self.agent.ask("오늘 서울 날씨 알려줘")["route"], "abstain")

    def test_feedback_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fb.jsonl"
            save_feedback("q", "a", "down", "정답은 b", path=p)
            row = json.loads(p.read_text(encoding="utf-8").splitlines()[0])
            self.assertEqual(row["rating"], "down")
        with self.assertRaises(ValueError):
            save_feedback("q", "a", "meh", path="/dev/null")


class ServerTests(unittest.TestCase):
    def test_ask_endpoint(self):
        srv = make_server(0)
        port = srv.server_address[1]
        threading.Thread(target=srv.serve_forever, daemon=True).start()
        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{port}/ask",
                data=json.dumps({"question": "CVSS 점수 9.8은 어떤 등급이야?"}).encode(),
                headers={"Content-Type": "application/json"})
            body = json.loads(urllib.request.urlopen(req).read())
            self.assertIn("Critical", body["answer"])
        finally:
            srv.shutdown()


if __name__ == "__main__":
    unittest.main()
