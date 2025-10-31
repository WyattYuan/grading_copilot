"""
核心数据模型定义
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class ScoringCriterion(BaseModel):
    """评分标准项"""

    points: float = Field(description="该项的分数")
    criterion: str = Field(description="评分标准描述")


class Question(BaseModel):
    """题目配置"""

    id: str = Field(description="题目唯一ID")
    type: Literal["text", "code", "multimodal"] = Field(description="题目类型")
    description: str = Field(description="题目描述")
    attachments: Optional[List[str]] = Field(default=None, description="附件路径列表")
    max_score: float = Field(description="题目满分")
    reference_answer: str = Field(description="参考答案")
    scoring_criteria: List[ScoringCriterion] = Field(description="评分标准列表")
    code_snippet: Optional[str] = Field(
        default=None, description="初始代码(仅用于编程题)"
    )


class ExamConfig(BaseModel):
    """考试配置"""

    exam_title: str = Field(description="考试标题")
    questions: List[Question] = Field(description="题目列表")


class StudentAnswer(BaseModel):
    """学生答案"""

    student_id: str = Field(description="学生ID")
    answers: dict[str, str] = Field(
        description="答案字典, key为题目ID, value为答案内容"
    )


class GradingResult(BaseModel):
    """AI评分结果(结构化输出)"""

    score: float = Field(description="基于评分标准给出的分数")
    rationale: str = Field(description="详细的评分依据,必须逐条对比评分标准")


class QuestionSnapshot(BaseModel):
    """题目快照(用于报告)"""

    description: str
    max_score: float
    reference_answer: str


class GradingReport(BaseModel):
    """评分报告(单个题目)"""

    student_id: str
    question_id: str
    task_id: str
    question_snapshot: QuestionSnapshot
    student_answer: str

    ai_score: float = Field(description="AI的原始评分")
    ai_rationale: str = Field(description="AI的评分依据")

    final_score: float = Field(description="最终生效的分数")
    human_override_rationale: Optional[str] = Field(
        default=None, description="教师微调评语"
    )
    last_modified_by: str = Field(default="AI", description="最后修改者")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class JobStatus(BaseModel):
    """任务状态"""

    job_id: str
    status: Literal["pending", "running", "completed", "failed"]
    total_questions: int
    processed_questions: int
    created_at: datetime
    updated_at: datetime
    error_message: Optional[str] = None


class UpdateReportRequest(BaseModel):
    """更新报告请求"""

    new_score: float = Field(ge=0, description="新分数")
    new_rationale: str = Field(description="修改理由")
    modified_by: str = Field(default="Teacher", description="修改者")
