"""
文件处理工具
"""

import json
import re
import zipfile
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from docx import Document
from src.models import ExamConfig, StudentAnswer, GradingReport
from src.config import config


class FileParser:
    """文件解析器"""

    @staticmethod
    def parse_exam_config(file_path: Path) -> ExamConfig:
        """
        解析考试配置JSON文件

        Args:
            file_path: JSON文件路径

        Returns:
            ExamConfig: 考试配置对象
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ExamConfig(**data)

    @staticmethod
    def parse_student_answer_txt(file_path: Path) -> Dict[str, str]:
        """
        解析TXT格式的学生答案

        格式示例:
        [作答: q1]
        这是第一题的答案

        [作答: q2]
        这是第二题的答案

        Args:
            file_path: TXT文件路径

        Returns:
            Dict[str, str]: 题目ID到答案的映射
        """
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # 使用正则表达式匹配答案块
        pattern = r"\[作答:\s*(\w+)\]\s*\n(.*?)(?=\[作答:|$)"
        matches = re.findall(pattern, content, re.DOTALL)

        answers = {}
        for question_id, answer_text in matches:
            answers[question_id.strip()] = answer_text.strip()

        return answers

    @staticmethod
    def parse_student_answer_docx(file_path: Path) -> Dict[str, str]:
        """
        解析DOCX格式的学生答案

        Args:
            file_path: DOCX文件路径

        Returns:
            Dict[str, str]: 题目ID到答案的映射
        """
        doc = Document(file_path)
        full_text = "\n".join([para.text for para in doc.paragraphs])

        # 使用与TXT相同的解析逻辑
        pattern = r"\[作答:\s*(\w+)\]\s*\n(.*?)(?=\[作答:|$)"
        matches = re.findall(pattern, full_text, re.DOTALL)

        answers = {}
        for question_id, answer_text in matches:
            answers[question_id.strip()] = answer_text.strip()

        return answers

    @staticmethod
    def parse_student_answer(file_path: Path) -> StudentAnswer:
        """
        自动识别文件格式并解析学生答案

        Args:
            file_path: 答案文件路径

        Returns:
            StudentAnswer: 学生答案对象
        """
        # 从文件名提取学生ID (假设格式为 student_XXX.txt 或 student_XXX.docx)
        student_id = file_path.stem  # 去掉扩展名的文件名

        # 根据扩展名选择解析方法
        if file_path.suffix.lower() == ".txt":
            answers = FileParser.parse_student_answer_txt(file_path)
        elif file_path.suffix.lower() == ".docx":
            answers = FileParser.parse_student_answer_docx(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {file_path.suffix}")

        return StudentAnswer(student_id=student_id, answers=answers)

    @staticmethod
    def extract_zip(zip_path: Path, extract_to: Path) -> List[Path]:
        """
        解压ZIP文件并返回所有学生答案文件路径

        Args:
            zip_path: ZIP文件路径
            extract_to: 解压目标目录

        Returns:
            List[Path]: 学生答案文件路径列表
        """
        extract_to.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall(extract_to)

        # 查找所有txt和docx文件
        answer_files = []
        for pattern in ["*.txt", "*.docx"]:
            answer_files.extend(extract_to.glob(pattern))
            # 也搜索子目录
            answer_files.extend(extract_to.glob(f"**/{pattern}"))

        return answer_files


class ReportManager:
    """报告管理器"""

    @staticmethod
    def save_report(report: GradingReport, job_id: str) -> Path:
        """
        保存评分报告

        Args:
            report: 评分报告对象
            job_id: 任务ID

        Returns:
            Path: 保存的文件路径
        """
        # 创建任务目录
        job_dir = config.REPORTS_DIR / job_id
        job_dir.mkdir(parents=True, exist_ok=True)

        # 文件名格式: report_studentID_questionID.json
        filename = f"report_{report.student_id}_{report.question_id}.json"
        file_path = job_dir / filename

        # 保存为JSON
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(report.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

        return file_path

    @staticmethod
    def load_report(job_id: str, student_id: str, question_id: str) -> GradingReport:
        """
        加载评分报告

        Args:
            job_id: 任务ID
            student_id: 学生ID
            question_id: 题目ID

        Returns:
            GradingReport: 评分报告对象
        """
        filename = f"report_{student_id}_{question_id}.json"
        file_path = config.REPORTS_DIR / job_id / filename

        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return GradingReport(**data)

    @staticmethod
    def get_all_reports(job_id: str) -> List[GradingReport]:
        """
        获取任务的所有报告

        Args:
            job_id: 任务ID

        Returns:
            List[GradingReport]: 报告列表
        """
        job_dir = config.REPORTS_DIR / job_id
        if not job_dir.exists():
            return []

        reports = []
        for report_file in job_dir.glob("report_*.json"):
            with open(report_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            reports.append(GradingReport(**data))

        return reports

    @staticmethod
    def update_report(
        job_id: str,
        student_id: str,
        question_id: str,
        new_score: float,
        new_rationale: str,
        modified_by: str,
    ) -> GradingReport:
        """
        更新评分报告

        Args:
            job_id: 任务ID
            student_id: 学生ID
            question_id: 题目ID
            new_score: 新分数
            new_rationale: 修改理由
            modified_by: 修改者

        Returns:
            GradingReport: 更新后的报告
        """
        from datetime import datetime

        # 加载原报告
        report = ReportManager.load_report(job_id, student_id, question_id)

        # 更新字段
        report.final_score = new_score
        report.human_override_rationale = new_rationale
        report.last_modified_by = modified_by
        report.updated_at = datetime.now()

        # 保存
        ReportManager.save_report(report, job_id)

        return report


def get_all_jobs() -> list:
    """
    获取所有任务列表

    Returns:
        list: 任务列表，每个任务包含job_id, status, created_at等信息
    """
    jobs = []
    uploads_dir = config.UPLOADS_DIR

    if not uploads_dir.exists():
        return jobs

    for job_dir in uploads_dir.iterdir():
        if job_dir.is_dir() and job_dir.name.startswith("job_"):
            job_id = job_dir.name

            # 尝试读取考试配置获取更多信息
            exam_config_path = job_dir / "exam_config.json"
            created_at = None
            exam_name = None

            if exam_config_path.exists():
                try:
                    # 使用文件修改时间作为创建时间
                    created_at = datetime.fromtimestamp(
                        exam_config_path.stat().st_ctime
                    ).isoformat()

                    # 尝试从配置中获取考试名称
                    with open(exam_config_path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                        exam_name = config_data.get("exam_name", "")
                except:
                    pass

            # 统计学生数量
            answers_dir = job_dir / "answers"
            student_count = 0
            if answers_dir.exists():
                student_count = len(list(answers_dir.glob("student_*.*")))

            jobs.append(
                {
                    "job_id": job_id,
                    "created_at": created_at or job_id,  # 如果没有时间，使用job_id排序
                    "exam_name": exam_name,
                    "student_count": student_count,
                }
            )

    # 按创建时间倒序排列（最新的在前面）
    jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return jobs


def save_job_status(job_id: str, status_data: dict):
    """
    保存任务状态到文件

    Args:
        job_id: 任务ID
        status_data: 状态数据（字典格式）
    """
    job_dir = config.UPLOADS_DIR / job_id
    job_dir.mkdir(parents=True, exist_ok=True)

    status_file = job_dir / "status.json"
    with open(status_file, "w", encoding="utf-8") as f:
        json.dump(status_data, f, ensure_ascii=False, indent=2, default=str)


def load_job_status(job_id: str) -> dict:
    """
    从文件加载任务状态

    Args:
        job_id: 任务ID

    Returns:
        dict: 状态数据，如果不存在返回None
    """
    status_file = config.UPLOADS_DIR / job_id / "status.json"

    if not status_file.exists():
        return None

    with open(status_file, "r", encoding="utf-8") as f:
        return json.load(f)


def job_exists(job_id: str) -> bool:
    """
    检查任务是否存在

    Args:
        job_id: 任务ID

    Returns:
        bool: 任务是否存在
    """
    job_dir = config.UPLOADS_DIR / job_id
    return job_dir.exists() and job_dir.is_dir()
