"""
文件处理工具
"""

import json
import re
import zipfile
from pathlib import Path
from typing import Dict, List
from datetime import datetime
from abc import ABC, abstractmethod
from docx import Document
from src.models import ExamConfig, StudentAnswer, GradingReport, StudentInfo
from src.config import config


class BaseStudentAnswerParser(ABC):
    """学生答案解析器基类"""

    @abstractmethod
    def read_content(self, file_path: Path) -> str:
        """
        读取文件内容为文本

        Args:
            file_path: 文件路径

        Returns:
            str: 文件文本内容
        """
        pass

    def parse(self, file_path: Path) -> Dict[str, str]:
        """
        解析学生答案文件

        Args:
            file_path: 文件路径

        Returns:
            Dict[str, str]: 包含学生信息和题目答案的映射
        """
        # 读取内容
        content = self.read_content(file_path)

        # 提取学生信息
        result = self._extract_student_info(content)

        # 提取答案
        answers = self._extract_answers(content)
        result.update(answers)

        return result

    def _extract_student_info(self, content: str) -> Dict[str, str]:
        """
        提取学生信息

        Args:
            content: 文件内容

        Returns:
            Dict[str, str]: 学生信息字典
        """
        result = {}

        # 提取姓名
        name_match = re.search(r"学生姓名[:：]\s*(.+)", content)
        if name_match:
            result["student_name"] = name_match.group(1).strip()

        # 提取学号
        id_match = re.search(r"学号[:：]\s*(.+)", content)
        if id_match:
            result["student_id"] = id_match.group(1).strip()

        # 提取性别
        gender_match = re.search(r"性别[:：]\s*(.+)", content)
        if gender_match:
            result["student_gender"] = gender_match.group(1).strip()

        return result

    def _extract_answers(self, content: str) -> Dict[str, str]:
        """
        提取题目答案

        Args:
            content: 文件内容

        Returns:
            Dict[str, str]: 题目ID到答案的映射
        """
        result = {}
        pattern = r"\[作答:\s*(\w+)\]\s*\n(.*?)(?=\[作答:|$)"
        matches = re.findall(pattern, content, re.DOTALL)

        for question_id, answer_text in matches:
            result[question_id.strip()] = answer_text.strip()

        return result


class TxtStudentAnswerParser(BaseStudentAnswerParser):
    """TXT格式学生答案解析器"""

    def read_content(self, file_path: Path) -> str:
        """读取TXT文件内容"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


class DocxStudentAnswerParser(BaseStudentAnswerParser):
    """DOCX格式学生答案解析器"""

    def read_content(self, file_path: Path) -> str:
        """读取DOCX文件内容"""
        doc = Document(str(file_path))
        return "\n".join([para.text for para in doc.paragraphs])


class MarkdownStudentAnswerParser(BaseStudentAnswerParser):
    """Markdown格式学生答案解析器"""

    def read_content(self, file_path: Path) -> str:
        """读取Markdown文件内容"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()


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

    # 解析器映射
    _parsers = {
        ".txt": TxtStudentAnswerParser(),
        ".docx": DocxStudentAnswerParser(),
        ".md": MarkdownStudentAnswerParser(),
    }

    @staticmethod
    def parse_student_answer(file_path: Path) -> StudentAnswer:
        """
        自动识别文件格式并解析学生答案

        Args:
            file_path: 答案文件路径

        Returns:
            StudentAnswer: 学生答案对象
        """
        # 获取对应的解析器
        suffix = file_path.suffix.lower()
        parser = FileParser._parsers.get(suffix)

        if parser is None:
            raise ValueError(f"不支持的文件格式: {suffix}")

        # 解析文件
        parsed_data = parser.parse(file_path)

        # 提取学生信息
        student_info = StudentInfo(
            student_id=parsed_data.get("student_id", file_path.stem),
            student_name=parsed_data.get("student_name", "未填写"),
            student_gender=parsed_data.get("student_gender", "未填写"),
        )

        # 提取答案（排除学生信息字段）
        answers = {
            k: v
            for k, v in parsed_data.items()
            if k not in ["student_id", "student_name", "student_gender"]
        }

        return StudentAnswer(student_info=student_info, answers=answers)

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

        # 查找所有 txt、docx 和 md 文件（包括子目录）
        answer_files = []
        for pattern in ["**/*.txt", "**/*.docx", "**/*.md"]:
            answer_files.extend(extract_to.glob(pattern))

        # 去重（使用set去除可能的重复路径）
        answer_files = list(set(answer_files))

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
        filename = f"report_{report.student_info.student_id}_{report.question_id}.json"
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

            # 优先尝试从 status.json 读取完整信息
            status_file = job_dir / "status.json"
            if status_file.exists():
                try:
                    status_data = load_job_status(job_id)
                    if status_data:
                        jobs.append(status_data)
                        continue
                except:
                    pass

            # 如果没有status.json，尝试从exam_config.json构建基本信息
            exam_config_path = job_dir / "exam_config.json"
            created_at = None
            exam_title = None

            if exam_config_path.exists():
                try:
                    # 使用文件修改时间作为创建时间
                    created_at = datetime.fromtimestamp(
                        exam_config_path.stat().st_ctime
                    ).isoformat()

                    # 从配置中获取考试标题
                    with open(exam_config_path, "r", encoding="utf-8") as f:
                        config_data = json.load(f)
                        exam_title = config_data.get("exam_title", "")
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
                    "exam_title": exam_title,
                    "student_count": student_count,
                    "status": "unknown",  # 没有status.json时标记为unknown
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


def load_job_status(job_id: str) -> dict | None:
    """
    从文件加载任务状态

    Args:
        job_id: 任务ID

    Returns:
        dict | None: 状态数据，如果不存在返回None
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
