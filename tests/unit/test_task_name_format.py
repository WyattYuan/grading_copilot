"""
测试任务名称格式化功能
"""

import sys
from pathlib import Path

# 添加src到路径
sys.path.append(str(Path(__file__).parent.parent))


def test_format_job_display_name():
    """测试任务显示名称格式化"""
    from src.ui.app import format_job_display_name

    # 测试用例1: 完整信息
    job1 = {
        "job_id": "job_a25bff38150a",
        "exam_title": "Python程序设计期中考试",
        "created_at": "2025-11-01T14:30:25.123456",
        "student_count": 5,
    }
    result1 = format_job_display_name(job1)
    print(f"测试1 - 完整信息:")
    print(f"  输入: {job1}")
    print(f"  输出: {result1}")
    print(f"  预期: Python程序设计期中考试 (2025-11-01 14:30:25) [5人]")
    assert "Python程序设计期中考试" in result1
    assert "2025-11-01 14:30:25" in result1
    assert "[5人]" in result1
    print("  ✅ 通过\n")

    # 测试用例2: 不同时间（同一天）
    job2 = {
        "job_id": "job_b15e7f526f5a",
        "exam_title": "Python程序设计期中考试",
        "created_at": "2025-11-01T15:45:30.789012",
        "student_count": 5,
    }
    result2 = format_job_display_name(job2)
    print(f"测试2 - 同一天不同时间:")
    print(f"  输入: {job2}")
    print(f"  输出: {result2}")
    print(f"  预期: Python程序设计期中考试 (2025-11-01 15:45:30) [5人]")
    assert "15:45:30" in result2
    assert result1 != result2  # 确保不同时间的任务名称不同
    print("  ✅ 通过\n")

    # 测试用例3: 没有微秒的时间格式
    job3 = {
        "job_id": "job_c12345678901",
        "exam_title": "数据结构期末考试",
        "created_at": "2025-11-02T09:00:00",
        "student_count": 10,
    }
    result3 = format_job_display_name(job3)
    print(f"测试3 - 无微秒时间格式:")
    print(f"  输入: {job3}")
    print(f"  输出: {result3}")
    print(f"  预期: 数据结构期末考试 (2025-11-02 09:00:00) [10人]")
    assert "数据结构期末考试" in result3
    assert "2025-11-02 09:00:00" in result3
    assert "[10人]" in result3
    print("  ✅ 通过\n")

    # 测试用例4: 缺少考试名称
    job4 = {
        "job_id": "job_d98765432109",
        "created_at": "2025-11-03T16:20:15.456789",
        "student_count": 3,
    }
    result4 = format_job_display_name(job4)
    print(f"测试4 - 缺少考试名称:")
    print(f"  输入: {job4}")
    print(f"  输出: {result4}")
    print(f"  预期: 未命名考试 (2025-11-03 16:20:15) [3人]")
    assert "未命名考试" in result4
    assert "2025-11-03 16:20:15" in result4
    assert "[3人]" in result4
    print("  ✅ 通过\n")

    # 测试用例5: 缺少学生数量
    job5 = {
        "job_id": "job_e11111111111",
        "exam_title": "算法设计考试",
        "created_at": "2025-11-04T10:10:10.111111",
    }
    result5 = format_job_display_name(job5)
    print(f"测试5 - 缺少学生数量:")
    print(f"  输入: {job5}")
    print(f"  输出: {result5}")
    print(f"  预期: 算法设计考试 (2025-11-04 10:10:10)")
    assert "算法设计考试" in result5
    assert "2025-11-04 10:10:10" in result5
    assert "[" not in result5  # 没有学生数量部分
    print("  ✅ 通过\n")

    # 测试用例6: 缺少时间戳
    job6 = {
        "job_id": "job_f22222222222",
        "exam_title": "操作系统考试",
        "student_count": 8,
    }
    result6 = format_job_display_name(job6)
    print(f"测试6 - 缺少时间戳:")
    print(f"  输入: {job6}")
    print(f"  输出: {result6}")
    print(f"  预期: 操作系统考试 [8人]")
    assert "操作系统考试" in result6
    assert "[8人]" in result6
    assert "(" not in result6  # 没有时间部分
    print("  ✅ 通过\n")

    # 测试用例7: 只有考试名称
    job7 = {
        "job_id": "job_g33333333333",
        "exam_title": "计算机网络考试",
    }
    result7 = format_job_display_name(job7)
    print(f"测试7 - 只有考试名称:")
    print(f"  输入: {job7}")
    print(f"  输出: {result7}")
    print(f"  预期: 计算机网络考试")
    assert result7 == "计算机网络考试"
    print("  ✅ 通过\n")

    print("=" * 60)
    print("✅ 所有测试通过！")
    print("=" * 60)


if __name__ == "__main__":
    test_format_job_display_name()
