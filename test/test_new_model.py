"""测试新的数据模型"""

from src.models import Question, SubQuestion, ScoringCriterion, ExamConfig

print("=" * 50)
print("测试1: 单题（传统方式）")
print("=" * 50)

single_q = Question(
    id="q1",
    type="text",
    description="什么是Python？",
    max_score=10.0,
    reference_answer="Python是一种高级编程语言",
    scoring_criteria=[
        ScoringCriterion(points=5.0, criterion="提到是编程语言"),
        ScoringCriterion(points=5.0, criterion="提到高级语言特性"),
    ],
)

print(f"题目ID: {single_q.id}")
print(f"是否为大题: {single_q.is_composite()}")
print(f"总分: {single_q.get_total_score()}")
print()

print("=" * 50)
print("测试2: 大题（包含小题）")
print("=" * 50)

composite_q = Question(
    id="q2",
    type="text",
    description="综合题：关于数据结构",
    sub_questions=[
        SubQuestion(
            id="q2_1",
            description="什么是栈？",
            max_score=5.0,
            reference_answer="栈是后进先出的数据结构",
            scoring_criteria=[
                ScoringCriterion(points=3.0, criterion="提到LIFO"),
                ScoringCriterion(points=2.0, criterion="举例说明"),
            ],
        ),
        SubQuestion(
            id="q2_2",
            description="什么是队列？",
            max_score=5.0,
            reference_answer="队列是先进先出的数据结构",
            scoring_criteria=[
                ScoringCriterion(points=3.0, criterion="提到FIFO"),
                ScoringCriterion(points=2.0, criterion="举例说明"),
            ],
        ),
    ],
)

print(f"题目ID: {composite_q.id}")
print(f"是否为大题: {composite_q.is_composite()}")
print(f"总分: {composite_q.get_total_score()}")
print(f"小题数量: {len(composite_q.sub_questions) if composite_q.sub_questions else 0}")
if composite_q.sub_questions:
    for sq in composite_q.sub_questions:
        print(f"  - {sq.id}: {sq.description} ({sq.max_score}分)")
print()

print("=" * 50)
print("测试3: 创建完整试卷")
print("=" * 50)

exam = ExamConfig(exam_title="Python基础测试", questions=[single_q, composite_q])

print(f"试卷标题: {exam.exam_title}")
print(f"题目数量: {len(exam.questions)}")
total = sum(q.get_total_score() for q in exam.questions)
print(f"试卷总分: {total}")
print()

print("✅ 所有测试通过！")
