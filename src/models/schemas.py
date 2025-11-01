"""
核心数据模型定义 - 使用继承优化题目类型结构
"""

from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime


class ScoringCriterion(BaseModel):
    """评分标准项"""

    points: float = Field(description="该项的分数")
    criterion: str = Field(description="评分标准描述")


# ============================================================================
# 题目基类和具体实现（使用继承）
# ============================================================================


class QuestionBase(BaseModel):
    """题目基类 - 定义所有题目的共同属性"""

    id: str = Field(description="题目唯一ID")
    type: Literal["text", "code", "multimodal"] = Field(description="题目类型")
    description: str = Field(description="题目描述")
    attachments: Optional[List[str]] = Field(default=None, description="附件路径列表")

    def get_total_score(self) -> float:
        """获取题目总分（由子类覆盖或使用默认逻辑）"""
        raise NotImplementedError("子类必须实现此方法")

    def is_composite(self) -> bool:
        """判断是否为复合题（包含小题）"""
        raise NotImplementedError("子类必须实现此方法")


class SubQuestion(BaseModel):
    """小题（子问题）"""

    id: str = Field(description="小题ID，如 q1_1, q1_2")
    description: str = Field(description="小题描述")
    max_score: float = Field(description="小题满分")
    reference_answer: str = Field(description="参考答案")
    scoring_criteria: List[ScoringCriterion] = Field(description="评分标准列表")

    def get_scoring_criteria_text(self) -> str:
        """获取格式化的评分标准文本"""
        if not self.scoring_criteria:
            return "暂无评分标准"

        lines = []
        for idx, criterion in enumerate(self.scoring_criteria, 1):
            lines.append(f"{idx}. ({criterion.points}分) {criterion.criterion}")
        return "\n".join(lines)


class Question(QuestionBase):
    """题目配置（支持单题和复合题，向后兼容原有设计）

    设计说明：
    - 单题：必须有 max_score, reference_answer, scoring_criteria
    - 复合题：必须有 sub_questions，其他字段为None
    """

    # 单题字段
    max_score: Optional[float] = Field(default=None, description="单题满分")
    reference_answer: Optional[str] = Field(default=None, description="单题参考答案")
    scoring_criteria: Optional[List[ScoringCriterion]] = Field(
        default=None, description="单题评分标准"
    )
    code_snippet: Optional[str] = Field(
        default=None, description="初始代码(仅用于编程题)"
    )

    # 复合题字段
    sub_questions: Optional[List[SubQuestion]] = Field(
        default=None, description="小题列表，如果有则为大题"
    )

    @model_validator(mode="after")
    def validate_question_type(self):
        """验证题目类型的一致性"""
        is_simple = self.max_score is not None
        is_composite = self.sub_questions is not None and len(self.sub_questions) > 0

        # 必须是单题或复合题之一
        if is_simple == is_composite:
            if is_simple:
                raise ValueError(
                    "题目不能同时是单题和复合题（不能同时设置max_score和sub_questions）"
                )
            else:
                raise ValueError(
                    "题目必须是单题（设置max_score）或复合题（设置sub_questions）"
                )

        # 验证单题必须有的字段
        if is_simple:
            if self.reference_answer is None:
                raise ValueError("单题必须设置reference_answer")
            if self.scoring_criteria is None:
                raise ValueError("单题必须设置scoring_criteria")

        # 验证复合题至少有一个小题
        if (
            is_composite
            and self.sub_questions is not None
            and len(self.sub_questions) == 0
        ):
            raise ValueError("复合题必须至少包含一个小题")

        return self

    def is_composite(self) -> bool:
        """判断是否为大题（包含小题）"""
        return self.sub_questions is not None and len(self.sub_questions) > 0

    def get_total_score(self) -> float:
        """获取题目总分"""
        if self.is_composite() and self.sub_questions:
            return sum(sq.max_score for sq in self.sub_questions)
        return self.max_score or 0.0

    def get_max_score(self) -> float:
        """获取题目满分（单题直接返回，大题抛出异常）"""
        if self.is_composite():
            raise ValueError("大题没有单一满分，请使用 get_total_score()")
        if self.max_score is None:
            raise ValueError("单题必须有 max_score")
        return self.max_score

    def get_reference_answer(self) -> str:
        """获取参考答案（单题直接返回，大题抛出异常）"""
        if self.is_composite():
            raise ValueError("大题没有单一参考答案")
        if self.reference_answer is None:
            raise ValueError("单题必须有 reference_answer")
        return self.reference_answer

    def get_scoring_criteria(self) -> List[ScoringCriterion]:
        """获取评分标准（单题直接返回，大题抛出异常）"""
        if self.is_composite():
            raise ValueError("大题没有单一评分标准")
        if self.scoring_criteria is None:
            raise ValueError("单题必须有 scoring_criteria")
        return self.scoring_criteria

    def get_scoring_criteria_text(self) -> str:
        """获取格式化的评分标准文本"""
        if self.is_composite():
            return "大题包含多个小题，请查看各小题的评分标准"
        if not self.scoring_criteria:
            return "暂无评分标准"

        lines = []
        for idx, criterion in enumerate(self.scoring_criteria, 1):
            lines.append(f"{idx}. ({criterion.points}分) {criterion.criterion}")
        return "\n".join(lines)


# ============================================================================
# 考试配置和学生相关
# ============================================================================


class ExamConfig(BaseModel):
    """考试配置"""

    exam_title: str = Field(description="考试标题")
    questions: List[Question] = Field(description="题目列表")


class StudentInfo(BaseModel):
    """学生信息"""

    student_id: str = Field(description="学生学号")
    student_name: str = Field(description="学生姓名")
    student_gender: str = Field(description="学生性别")


class StudentAnswer(BaseModel):
    """学生答案"""

    student_info: StudentInfo = Field(description="学生信息")
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
    scoring_criteria: Optional[str] = Field(default=None, description="评分标准")


class GradingReport(BaseModel):
    """评分报告(单个题目)"""

    student_info: StudentInfo = Field(description="学生信息")
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

    # 新增字段：提升用户体验
    exam_title: Optional[str] = Field(default=None, description="考试标题")
    student_count: Optional[int] = Field(default=0, description="学生数量")


class UpdateReportRequest(BaseModel):
    """更新报告请求"""

    new_score: float = Field(ge=0, description="新分数")
    new_rationale: str = Field(description="修改理由")
    modified_by: str = Field(default="Teacher", description="修改者")
