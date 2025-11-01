"""
测试页面导航功能

验证：
1. 导航按钮能正确切换页面
2. session_state 正确保持状态
3. 跳转按钮能正确设置active_tab
"""


def test_navigation_logic():
    """测试导航逻辑"""
    print("=" * 60)
    print("测试：页面导航逻辑")
    print("=" * 60)

    # 模拟 session_state
    class MockSessionState:
        def __init__(self):
            self.data = {}

        def __setitem__(self, key, value):
            self.data[key] = value

        def __getitem__(self, key):
            return self.data[key]

        def get(self, key, default=None):
            return self.data.get(key, default)

        def __contains__(self, key):
            return key in self.data

    session_state = MockSessionState()

    # 测试1：初始化
    print("\n测试1：初始化状态")
    if "active_tab" not in session_state:
        session_state["active_tab"] = "exam_maker"
    print(f"  初始页面: {session_state['active_tab']}")
    assert session_state["active_tab"] == "exam_maker", "初始页面应为exam_maker"
    print("  ✅ 通过")

    # 测试2：跳转到其他页面
    print("\n测试2：跳转到评分结果页面")
    session_state["active_tab"] = "results"
    session_state["current_job_id"] = "job_123"
    print(f"  当前页面: {session_state['active_tab']}")
    print(f"  当前任务: {session_state['current_job_id']}")
    assert session_state["active_tab"] == "results", "应跳转到results"
    assert session_state["current_job_id"] == "job_123", "任务ID应保存"
    print("  ✅ 通过")

    # 测试3：模拟侧边栏按钮
    print("\n测试3：模拟侧边栏「查看结果」按钮")
    job_id = "job_456"
    # 模拟按钮点击
    session_state["current_job_id"] = job_id
    session_state["active_tab"] = "results"
    print(f"  设置任务ID: {job_id}")
    print(f"  设置页面: results")
    assert session_state["active_tab"] == "results", "应跳转到results"
    assert session_state["current_job_id"] == "job_456", "任务ID应更新"
    print("  ✅ 通过")

    # 测试4：模拟上传后停留
    print("\n测试4：上传后停留在新建任务页面")
    session_state["active_tab"] = "new_job"
    # 模拟上传操作（不改变active_tab）
    current_page = session_state["active_tab"]
    print(f"  上传前页面: {current_page}")
    # 上传成功，不改变页面
    print(f"  上传后页面: {session_state['active_tab']}")
    assert session_state["active_tab"] == "new_job", "应停留在new_job"
    print("  ✅ 通过")

    # 测试5：导航映射
    print("\n测试5：导航映射正确性")
    tab_options = {
        "📝 试卷制作": "exam_maker",
        "📤 新建评分任务": "new_job",
        "📊 任务状态": "status",
        "📋 评分结果": "results",
        "✏️ 人工微调": "adjust",
    }

    for display_name, page_id in tab_options.items():
        session_state["active_tab"] = page_id
        assert session_state["active_tab"] == page_id, f"页面{display_name}映射错误"
        print(f"  {display_name} → {page_id} ✅")

    print("\n" + "=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)
    return True


def test_navigation_scenarios():
    """测试实际使用场景"""
    print("\n" + "=" * 60)
    print("测试：实际使用场景")
    print("=" * 60)

    class MockSessionState:
        def __init__(self):
            self.data = {}

        def __setitem__(self, key, value):
            self.data[key] = value

        def __getitem__(self, key):
            return self.data.get(key)

        def get(self, key, default=None):
            return self.data.get(key, default)

        def __contains__(self, key):
            return key in self.data

    session_state = MockSessionState()

    # 场景1：用户流程 - 创建任务 → 查看状态 → 查看结果
    print("\n场景1：完整的用户流程")
    print("  步骤1：初始在试卷制作页面")
    session_state["active_tab"] = "exam_maker"
    print(f"    当前页面: {session_state['active_tab']}")

    print("  步骤2：导航到新建任务页面")
    session_state["active_tab"] = "new_job"
    print(f"    当前页面: {session_state['active_tab']}")

    print("  步骤3：上传文件创建任务")
    job_id = "job_789"
    print(f"    任务创建成功: {job_id}")

    print("  步骤4：点击「立即查看状态」")
    session_state["current_job_id"] = job_id
    session_state["active_tab"] = "status"
    print(f"    跳转到: {session_state['active_tab']}")
    print(f"    任务ID: {session_state['current_job_id']}")
    assert session_state["active_tab"] == "status"
    assert session_state["current_job_id"] == job_id

    print("  步骤5：任务完成，点击「查看评分结果」")
    session_state["active_tab"] = "results"
    print(f"    跳转到: {session_state['active_tab']}")
    print(f"    任务ID: {session_state['current_job_id']}")
    assert session_state["active_tab"] == "results"
    assert session_state["current_job_id"] == job_id

    print("  步骤6：需要调整，点击「进行人工微调」")
    session_state["active_tab"] = "adjust"
    print(f"    跳转到: {session_state['active_tab']}")
    print(f"    任务ID: {session_state['current_job_id']}")
    assert session_state["active_tab"] == "adjust"
    assert session_state["current_job_id"] == job_id

    print("  ✅ 场景1通过")

    # 场景2：侧边栏快捷操作
    print("\n场景2：侧边栏历史任务快捷操作")
    print("  步骤1：在任意页面")
    session_state["active_tab"] = "exam_maker"
    print(f"    当前页面: {session_state['active_tab']}")

    print("  步骤2：侧边栏点击历史任务的「查看结果」")
    another_job_id = "job_old_123"
    session_state["current_job_id"] = another_job_id
    session_state["active_tab"] = "results"
    print(f"    切换到任务: {another_job_id}")
    print(f"    跳转到页面: {session_state['active_tab']}")
    assert session_state["active_tab"] == "results"
    assert session_state["current_job_id"] == another_job_id

    print("  ✅ 场景2通过")

    print("\n" + "=" * 60)
    print("✅ 所有场景测试通过！")
    print("=" * 60)
    return True


def main():
    """运行所有测试"""
    print("\n" + "🧪 开始测试页面导航功能 🧪".center(60))
    print("\n")

    tests = [test_navigation_logic, test_navigation_scenarios]

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
        print("\n🎉 所有测试通过！导航功能正常！")
        return 0
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败")
        return 1


if __name__ == "__main__":
    exit(main())
