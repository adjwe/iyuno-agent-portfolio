"""에이전트가 호출하는 도구: 계산기, CVSS 등급 변환, (가상) 패치 정책 조회."""
from __future__ import annotations

import ast
import operator

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub,
    ast.Mult: operator.mul, ast.Div: operator.truediv,
}


def calculator(expr: str) -> float:
    """사칙연산만 허용하는 안전한 계산기 (eval 사용 안 함)."""
    def ev(node):
        if isinstance(node, ast.Expression):
            return ev(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return node.value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
            return _OPS[type(node.op)](ev(node.left), ev(node.right))
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.USub):
            return -ev(node.operand)
        raise ValueError("허용되지 않는 식")
    return ev(ast.parse(expr.strip(), mode="eval"))


def cvss_severity(score: float) -> str:
    """CVSS 점수(0.0~10.0)를 등급으로 변환한다."""
    if not 0.0 <= score <= 10.0:
        raise ValueError("CVSS 점수는 0.0~10.0 이어야 함")
    if score == 0.0:
        return "None"
    if score < 4.0:
        return "Low"
    if score < 7.0:
        return "Medium"
    if score < 9.0:
        return "High"
    return "Critical"


# 실제 조직의 정책이 아니라 과제용 '예시(가상)' 정책이다.
SAMPLE_PATCH_POLICY_DAYS = {"Critical": 3, "High": 7, "Medium": 30, "Low": 90}


def policy_lookup(severity: str) -> int:
    """등급별 패치 기한(일)을 반환한다."""
    if severity not in SAMPLE_PATCH_POLICY_DAYS:
        raise KeyError(f"정책 없음: {severity}")
    return SAMPLE_PATCH_POLICY_DAYS[severity]
