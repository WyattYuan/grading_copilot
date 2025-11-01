"""
测试模型重构和Bug修复

验证：
1. 模型验证器正确工作
2. 参考答案和评分标准能正确提取
3. QuestionSnapshot包含所有字段
"""

from src.models.schemas import (
    Question,
    ExamConfig,
    QuestionSnapshot,
    ScoringCriterion,
)
import json


def test_simple_question_validation():
    """测试单题验证"""
    print("=" * 60)
    print("测试1: 单题验证")
    print("=" * 60)

    # ✅ 有效的单题
    valid_simple = {
        "id": "q1",
        "type": "text",
        "description": "测试题目",
        "max_score": 10,
        "reference_answer": "测试答案",
        "scoring_criteria": [
            {"points": 5, "criterion": "标准1"},
            {"points": 5, "criterion": "标准2"},
        ],
    }

    try:
        q = Question.model_validate(valid_simple)
        print("✅ 有效单题加载成功")
        print(f"   - ID: {q.id}")
        print(f"   - 是否复合题: {q.is_composite()}")
        print(f"   - 满分: {q.get_max_score()}")
        print(f"   - 参考答案: {q.get_reference_answer()}")
        print(f"   - 评分标准:\n{q.get_scoring_criteria_text()}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

    # ❌ 无效：缺少reference_answer
    print("\n" + "-" * 60)
    invalid_simple = {
        "id": "q2",
        "type": "text",
        "description": "测试题目",
        "max_score": 10,
        # 缺少 reference_answer
        "scoring_criteria": [{"points": 10, "criterion": "标准"}],
    }

    try:
        q = Question.model_validate(invalid_simple)
        print("❌ 应该失败但成功了（缺少reference_answer）")
        return False
    except ValueError as e:
        print(f"✅ 正确拒绝无效数据: {e}")

    return True


def test_composite_question_validation():
    """测试复合题验证"""
    print("\n" + "=" * 60)
    print("测试2: 复合题验证")
    print("=" * 60)

    # ✅ 有效的复合题
    valid_composite = {
        "id": "q3",
        "type": "text",
        "description": "大题描述",
        "sub_questions": [
            {
                "id": "q3_1",
                "description": "小题1",
                "max_score": 5,
                "reference_answer": "答案1",
                "scoring_criteria": [{"points": 5, "criterion": "标准1"}],
            },
            {
                "id": "q3_2",
                "description": "小题2",
                "max_score": 5,
                "reference_answer": "答案2",
                "scoring_criteria": [{"points": 5, "criterion": "标准2"}],
            },
        ],
    }

    try:
        q = Question.model_validate(valid_composite)
        print("✅ 有效复合题加载成功")
        print(f"   - ID: {q.id}")
        print(f"   - 是否复合题: {q.is_composite()}")
        print(f"   - 总分: {q.get_total_score()}")
        print(f"   - 小题数量: {len(q.sub_questions)}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

    # ❌ 无效：sub_questions为空
    print("\n" + "-" * 60)
    invalid_composite = {
        "id": "q4",
        "type": "text",
        "description": "大题描述",
        "sub_questions": [],  # 空列表
    }

    try:
        q = Question.model_validate(invalid_composite)
        print("❌ 应该失败但成功了（sub_questions为空）")
        return False
    except ValueError as e:
        print(f"✅ 正确拒绝无效数据: {e}")

    return True


def test_mutual_exclusion():
    """测试单题和复合题互斥"""
    print("\n" + "=" * 60)
    print("测试3: 单题和复合题互斥验证")
    print("=" * 60)

    # ❌ 无效：同时设置单题和复合题字段
    invalid_mixed = {
        "id": "q5",
        "type": "text",
        "description": "混乱的题目",
        "max_score": 10,  # 单题字段
        "reference_answer": "答案",
        "scoring_criteria": [{"points": 10, "criterion": "标准"}],
        "sub_questions": [  # 复合题字段
            {
                "id": "q5_1",
                "description": "小题1",
                "max_score": 5,
                "reference_answer": "答案",
                "scoring_criteria": [{"points": 5, "criterion": "标准"}],
            }
        ],
    }

    try:
        q = Question.model_validate(invalid_mixed)
        print("❌ 应该失败但成功了（同时设置单题和复合题字段）")
        return False
    except ValueError as e:
        print(f"✅ 正确拒绝混合数据: {e}")

    return True


def test_real_exam_config():
    """测试真实的考试配置文件"""
    print("\n" + "=" * 60)
    print("测试4: 加载真实考试配置")
    print("=" * 60)

    try:
        with open("data/examples/test_exam_config.json", encoding="utf-8") as f:
            config_data = json.load(f)

        config = ExamConfig.model_validate(config_data)
        print(f"✅ 成功加载考试配置: {config.exam_title}")
        print(f"   - 题目数量: {len(config.questions)}")

        for i, q in enumerate(config.questions, 1):
            print(f"\n   题目 {i}:")
            print(f"   - ID: {q.id}")
            print(f"   - 类型: {q.type}")
            print(f"   - 是否复合题: {q.is_composite()}")
            if not q.is_composite():
                print(f"   - 满分: {q.get_max_score()}")
                print(f"   - 有参考答案: {len(q.get_reference_answer()) > 0}")
                print(f"   - 评分标准项数: {len(q.get_scoring_criteria())}")
            else:
                print(f"   - 总分: {q.get_total_score()}")
                print(f"   - 小题数: {len(q.sub_questions)}")

        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_question_snapshot_fields():
    """测试QuestionSnapshot包含所有必要字段"""
    print("\n" + "=" * 60)
    print("测试5: QuestionSnapshot字段完整性")
    print("=" * 60)

    # 创建一个简单题目
    question_data = {
        "id": "test",
        "type": "text",
        "description": "测试题",
        "max_score": 10,
        "reference_answer": "这是参考答案",
        "scoring_criteria": [
            {"points": 5, "criterion": "标准1"},
            {"points": 5, "criterion": "标准2"},
        ],
    }

    try:
        q = Question.model_validate(question_data)

        # 创建QuestionSnapshot（模拟API中的操作）
        snapshot = QuestionSnapshot(
            description=q.description,
            max_score=q.get_max_score(),
            reference_answer=q.get_reference_answer(),  # 关键字段
            scoring_criteria=q.get_scoring_criteria_text(),  # 关键字段
        )

        print("✅ QuestionSnapshot创建成功")
        print(f"   - description: {snapshot.description}")
        print(f"   - max_score: {snapshot.max_score}")
        print(f"   - reference_answer: {snapshot.reference_answer[:20]}...")
        print(f"   - scoring_criteria:\n{snapshot.scoring_criteria}")

        # 验证字段不为None
        assert snapshot.reference_answer is not None, "reference_answer 不应为 None"
        assert snapshot.scoring_criteria is not None, "scoring_criteria 不应为 None"
        print("\n✅ 所有关键字段都存在且非空")

        return True
    except Exception as e:
        print(f"❌ 失败: {e}")
        import traceback

        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "🧪 开始测试模型重构和Bug修复 🧪".center(60))
    print("\n")

    tests = [
        test_simple_question_validation,
        test_composite_question_validation,
        test_mutual_exclusion,
        test_real_exam_config,
        test_question_snapshot_fields,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n❌ 测试异常: {e}")
            import traceback

            traceback.print_exc()
            results.append(False)

    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")

    if passed == total:
        print("\n🎉 所有测试通过！模型重构成功！")
        return 0
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
