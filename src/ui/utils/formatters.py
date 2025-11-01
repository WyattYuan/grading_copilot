"""
格式化工具函数
"""

from typing import Dict, Any


def format_job_display_name(job: Dict[str, Any]) -> str:
    """格式化任务显示名称，使其更友好

    格式：考试标题 (YYYY-MM-DD HH:MM:SS) [N人]
    例如：Python程序设计期中考试 (2025-11-01 14:30:25) [5人]
    """
    exam_title = job.get("exam_title", "未命名考试")
    created_at = job.get("created_at", "")
    student_count = job.get("student_count", 0)

    # 提取完整的时间戳 (YYYY-MM-DD HH:MM:SS)
    # created_at 格式通常是 ISO 8601: 2025-11-01T14:30:25.123456
    if created_at:
        # 替换 T 为空格，并截取到秒（去掉微秒）
        if "T" in created_at:
            datetime_str = created_at.replace("T", " ").split(".")[0]
        else:
            datetime_str = (
                created_at.split(".")[0] if "." in created_at else created_at[:19]
            )
    else:
        datetime_str = ""

    # 格式：考试标题 (日期时间) [学生数]
    parts = [exam_title]
    if datetime_str:
        parts.append(f"({datetime_str})")
    if student_count > 0:
        parts.append(f"[{student_count}人]")

    return " ".join(parts)


def calculate_total_score(questions_data: list) -> float:
    """计算试卷总分"""
    total = 0.0
    for q in questions_data:
        if q.get("is_composite", False):
            # 大题：累加所有小题分数
            total += sum(sq["max_score"] for sq in q.get("sub_questions", []))
        else:
            # 单题
            total += q.get("max_score", 0.0)
    return total


def generate_answer_template(questions_data: list) -> str:
    """生成学生作答Markdown模板"""
    lines = ["# 学生作答模板", "", "**学生ID:** student_XXXX", "", "---", ""]

    for q in questions_data:
        is_composite = q.get("is_composite", False)

        if is_composite:
            # 大题
            lines.append(f"## {q['id']}. {q['description']}")
            lines.append("")

            for sq in q.get("sub_questions", []):
                lines.append(
                    f"### {sq['id']}. {sq['description']} ({sq['max_score']}分)"
                )
                lines.append("")
                lines.append(f"[作答: {sq['id']}]")
                lines.append("在此输入答案...")
                lines.append("")
        else:
            # 单题
            lines.append(f"## {q['id']}. {q['description']} ({q['max_score']}分)")
            lines.append("")
            lines.append(f"[作答: {q['id']}]")
            lines.append("在此输入答案...")
            lines.append("")

    return "\n".join(lines)
