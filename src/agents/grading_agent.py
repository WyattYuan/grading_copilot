"""
Langchain 智能评分代理
"""

from typing import Optional, cast
from langchain_openai import ChatOpenAI
from langchain_community.chat_models.tongyi import ChatTongyi
from langchain_core.prompts import ChatPromptTemplate
from pydantic import SecretStr
from src.models import Question, GradingResult
from src.config import config


class GradingAgent:
    """评分智能代理"""

    def __init__(self, model_name: Optional[str] = None, temperature: float = 0.0):
        """
        初始化评分代理

        Args:
            model_name: 模型名称,默认使用配置中的模型
            temperature: 温度参数,默认为0以保证评分一致性
        """
        self.model_name = model_name or config.OPENAI_MODEL
        self.llm = ChatTongyi(
            model=self.model_name,
            # temperature=temperature,
            api_key=SecretStr(config.OPENAI_API_KEY),
        )

        # 绑定结构化输出
        self.structured_llm = self.llm.with_structured_output(GradingResult)

        # 创建 Prompt 模板
        self.prompt = ChatPromptTemplate.from_messages(
            [("system", self._get_system_prompt()), ("human", self._get_human_prompt())]
        )

        # 创建评分链
        self.grading_chain = self.prompt | self.structured_llm

    def _get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个严格的、专业的课程助教。
你的任务是根据 [评分标准] 来评判 [学生作答]。

重要规则:
1. [参考答案] 仅供你参考理解题意，[评分标准] 才是你给分的唯一依据
2. 必须逐条对比评分标准，给出详细的评分依据
3. 评分必须严格、公正、一致
4. 如果学生答案与参考答案表述不同但意思正确，也应该给分
5. 必须指出学生答案的优点和不足
6. 总分不能超过题目满分"""

    def _get_human_prompt(self) -> str:
        """获取用户提示词模板"""
        return """【题目描述】
{question_description}

【题目满分】
{max_score} 分

【参考答案】
{reference_answer}

【评分标准】
{scoring_criteria}

【学生作答】
{student_answer}

请严格按照评分标准，给出你的评分和详细依据。评分依据必须逐条说明学生在每个评分标准上的表现。"""

    def _format_scoring_criteria(self, question: Question) -> str:
        """格式化评分标准为易读字符串"""
        criteria = question.get_scoring_criteria()
        criteria_lines = []
        for i, criterion in enumerate(criteria, 1):
            criteria_lines.append(f"{i}. [{criterion.points}分] {criterion.criterion}")
        return "\n".join(criteria_lines)

    async def grade(self, question: Question, student_answer: str) -> GradingResult:
        """
        对单个题目的学生答案进行评分

        Args:
            question: 题目对象（必须是单题，不能是大题）
            student_answer: 学生答案

        Returns:
            GradingResult: 包含分数和评分依据的结构化结果
        """
        # 准备输入变量
        input_vars = {
            "question_description": question.description,
            "max_score": question.get_max_score(),
            "reference_answer": question.get_reference_answer(),
            "scoring_criteria": self._format_scoring_criteria(question),
            "student_answer": student_answer,
        }

        # 调用评分链
        result = cast(GradingResult, await self.grading_chain.ainvoke(input_vars))

        # 确保分数不超过满分
        max_score = question.get_max_score()
        if result.score > max_score:
            result.score = max_score

        # 确保分数不为负
        if result.score < 0:
            result.score = 0

        return result

    def grade_sync(self, question: Question, student_answer: str) -> GradingResult:
        """
        同步版本的评分方法

        Args:
            question: 题目对象（必须是单题，不能是大题）
            student_answer: 学生答案

        Returns:
            GradingResult: 包含分数和评分依据的结构化结果
        """
        # 准备输入变量
        input_vars = {
            "question_description": question.description,
            "max_score": question.get_max_score(),
            "reference_answer": question.get_reference_answer(),
            "scoring_criteria": self._format_scoring_criteria(question),
            "student_answer": student_answer,
        }

        # 调用评分链
        result = cast(GradingResult, self.grading_chain.invoke(input_vars))

        # 确保分数不超过满分
        max_score = question.get_max_score()
        if result.score > max_score:
            result.score = max_score

        # 确保分数不为负
        if result.score < 0:
            result.score = 0

        return result
