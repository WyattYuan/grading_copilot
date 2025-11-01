"""
数据同步管理器 - 确保报告与总分表的一致性
"""

import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from src.models import GradingReport
from src.api.file_utils import ReportManager
from src.config import config


class SyncManager:
    """数据同步管理器 - 核心功能是确保总分表始终由报告动态生成"""

    @staticmethod
    def regenerate_summary_table(job_id: str) -> Path:
        """
        重新生成总分表 (核心方法)

        这个方法会:
        1. 遍历该任务的所有报告文件
        2. 读取每份报告的 final_score
        3. 汇总生成 CSV 总分表

        Args:
            job_id: 任务ID

        Returns:
            Path: 生成的CSV文件路径
        """
        # 获取所有报告
        reports = ReportManager.get_all_reports(job_id)

        if not reports:
            raise ValueError(f"任务 {job_id} 没有找到任何报告")

        # 按学生ID分组,汇总每个学生的分数
        student_scores: Dict[str, Dict[str, Any]] = {}

        for report in reports:
            student_id = report.student_info.student_id
            question_id = report.question_id
            final_score = report.final_score

            if student_id not in student_scores:
                student_scores[student_id] = {
                    "student_name": report.student_info.student_name,
                    "student_gender": report.student_info.student_gender,
                    "scores": {},
                }

            student_scores[student_id]["scores"][question_id] = final_score

        # 构建DataFrame
        rows = []
        for student_id, data in student_scores.items():
            row: Dict[str, Any] = {
                "student_id": student_id,
                "student_name": data["student_name"],
                "student_gender": data["student_gender"],
            }

            # 添加每道题的分数
            for q_id, score in sorted(data["scores"].items()):
                row[f"{q_id}_score"] = score

            # 计算总分
            row["total_score"] = sum(data["scores"].values())

            rows.append(row)

        # 创建DataFrame并按student_id排序
        df = pd.DataFrame(rows)
        df = df.sort_values("student_id")

        # 保存为CSV
        job_dir = config.REPORTS_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)
        csv_path = job_dir / "summary_table.csv"

        df.to_csv(
            csv_path, index=False, encoding="utf-8-sig"
        )  # utf-8-sig 确保Excel正确显示中文

        return csv_path

    @staticmethod
    def get_summary_table(job_id: str) -> pd.DataFrame:
        """
        获取总分表的DataFrame

        Args:
            job_id: 任务ID

        Returns:
            pd.DataFrame: 总分表
        """
        csv_path = config.REPORTS_DIR / job_id / "summary_table.csv"

        if not csv_path.exists():
            # 如果不存在,则生成
            SyncManager.regenerate_summary_table(job_id)

        return pd.read_csv(csv_path)

    @staticmethod
    def on_report_updated(job_id: str):
        """
        报告更新后的回调 - 自动重新生成总分表

        这是确保数据一致性的关键:
        每次报告被修改后,立即调用此方法重新生成总分表

        Args:
            job_id: 任务ID
        """
        SyncManager.regenerate_summary_table(job_id)

    @staticmethod
    def get_student_detail(job_id: str, student_id: str) -> Dict:
        """
        获取某个学生的详细评分信息

        Args:
            job_id: 任务ID
            student_id: 学生ID

        Returns:
            Dict: 包含所有题目的详细评分
        """
        reports = ReportManager.get_all_reports(job_id)

        student_reports = [
            r for r in reports if r.student_info.student_id == student_id
        ]

        if not student_reports:
            return {"student_id": student_id, "questions": [], "total_score": 0.0}

        # 从第一个报告中获取学生信息
        first_report = student_reports[0]
        result = {
            "student_id": student_id,
            "student_name": first_report.student_info.student_name,
            "student_gender": first_report.student_info.student_gender,
            "questions": [],
            "total_score": 0.0,
        }

        for report in sorted(student_reports, key=lambda x: x.question_id):
            result["questions"].append(
                {
                    "question_id": report.question_id,
                    "question_description": report.question_snapshot.description,
                    "max_score": report.question_snapshot.max_score,
                    "reference_answer": report.question_snapshot.reference_answer,  # 添加参考答案
                    "scoring_criteria": report.question_snapshot.scoring_criteria,  # 添加评分标准
                    "student_answer": report.student_answer,
                    "ai_score": report.ai_score,
                    "ai_rationale": report.ai_rationale,
                    "final_score": report.final_score,
                    "human_override_rationale": report.human_override_rationale,
                    "last_modified_by": report.last_modified_by,
                }
            )
            result["total_score"] += report.final_score

        return result
