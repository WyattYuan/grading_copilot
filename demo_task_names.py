"""
演示任务名称显示效果
"""

from datetime import datetime, timedelta
import random


def generate_sample_jobs():
    """生成示例任务数据"""
    exams = [
        "Python程序设计期中考试",
        "数据结构期末考试",
        "算法设计与分析",
        "操作系统原理",
        "计算机网络",
    ]

    base_time = datetime(2025, 11, 1, 9, 0, 0)
    jobs = []

    for i, exam_title in enumerate(exams):
        # 同一天的不同时间
        for j in range(3):
            job_time = base_time + timedelta(
                hours=i * 3, minutes=j * 15, seconds=j * 10
            )
            student_count = random.randint(3, 10)

            job = {
                "job_id": f"job_{random.randint(100000000000, 999999999999):012x}",
                "exam_title": exam_title,
                "created_at": job_time.isoformat(),
                "student_count": student_count,
                "status": "completed",
            }
            jobs.append(job)

    return jobs


def format_job_display_name(job):
    """格式化任务显示名称（复制自app.py）"""
    exam_title = job.get("exam_title", "未命名考试")
    created_at = job.get("created_at", "")
    student_count = job.get("student_count", 0)

    # 提取完整的时间戳
    if created_at:
        if "T" in created_at:
            datetime_str = created_at.replace("T", " ").split(".")[0]
        else:
            datetime_str = (
                created_at.split(".")[0] if "." in created_at else created_at[:19]
            )
    else:
        datetime_str = ""

    # 格式：考试标题 (日期时间) [学生数]
    parts = [exam_title]
    if datetime_str:
        parts.append(f"({datetime_str})")
    if student_count > 0:
        parts.append(f"[{student_count}人]")

    return " ".join(parts)


def main():
    """主函数 - 演示效果"""
    print("=" * 80)
    print("📋 任务名称显示效果演示")
    print("=" * 80)
    print()

    jobs = generate_sample_jobs()

    # 按时间排序
    jobs.sort(key=lambda x: x["created_at"])

    print("🎯 新格式效果预览：")
    print("-" * 80)
    print()

    for i, job in enumerate(jobs, 1):
        display_name = format_job_display_name(job)
        print(f"{i:2d}. {display_name}")

    print()
    print("-" * 80)
    print()

    # 特别展示：同一考试的多次运行
    print("🔍 重点：同一考试的多次运行（可以清楚区分）")
    print("-" * 80)
    print()

    python_jobs = [j for j in jobs if "Python" in j["exam_title"]]
    for i, job in enumerate(python_jobs, 1):
        display_name = format_job_display_name(job)
        print(f"  第{i}次运行: {display_name}")

    print()
    print("-" * 80)
    print()

    # 对比展示
    print("📊 优化前后对比")
    print("-" * 80)
    print()

    sample_job = python_jobs[0]
    old_format = f"{sample_job['exam_title']} ({sample_job['created_at'][:10]})"
    new_format = format_job_display_name(sample_job)

    print(f"❌ 旧格式: {old_format}")
    print(f"   问题：同一天的任务无法区分")
    print()
    print(f"✅ 新格式: {new_format}")
    print(f"   优势：时间精确到秒 + 显示学生数")
    print()

    print("-" * 80)
    print()

    # 统计信息
    print("📈 任务统计")
    print("-" * 80)
    print()
    print(f"总任务数: {len(jobs)}")
    print(f"不同考试: {len(set(j['exam_title'] for j in jobs))}")
    print(f"时间跨度: {jobs[0]['created_at'][:10]} ~ {jobs[-1]['created_at'][:10]}")
    print(f"平均学生数: {sum(j['student_count'] for j in jobs) / len(jobs):.1f}人")
    print()

    print("=" * 80)
    print("✅ 演示完成！新格式能够完美区分所有任务。")
    print("=" * 80)


if __name__ == "__main__":
    main()
