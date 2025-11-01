"""
测试任务数据读取
"""

import sys
from pathlib import Path
import json

# 添加src到路径
sys.path.append(str(Path(__file__).parent.parent))

from src.config import config
from src.api.file_utils import get_all_jobs, load_job_status


def main():
    print("=" * 80)
    print("📋 检查任务数据")
    print("=" * 80)
    print()

    # 1. 检查uploads目录
    uploads_dir = config.UPLOADS_DIR
    print(f"📁 上传目录: {uploads_dir}")
    print(f"   存在: {uploads_dir.exists()}")
    print()

    if not uploads_dir.exists():
        print("❌ 上传目录不存在！")
        return

    # 2. 列出所有job目录
    job_dirs = [
        d for d in uploads_dir.iterdir() if d.is_dir() and d.name.startswith("job_")
    ]
    print(f"📂 找到 {len(job_dirs)} 个任务目录:")
    for job_dir in job_dirs:
        print(f"   - {job_dir.name}")
    print()

    # 3. 检查每个任务的文件
    for job_dir in job_dirs:
        job_id = job_dir.name
        print(f"🔍 检查任务: {job_id}")
        print(f"   {'='*70}")

        # status.json
        status_file = job_dir / "status.json"
        print(f"   📄 status.json: {status_file.exists()}")
        if status_file.exists():
            with open(status_file, "r", encoding="utf-8") as f:
                status_data = json.load(f)
                print(f"      - exam_title: {status_data.get('exam_title', 'N/A')}")
                print(
                    f"      - student_count: {status_data.get('student_count', 'N/A')}"
                )
                print(f"      - created_at: {status_data.get('created_at', 'N/A')}")
                print(f"      - status: {status_data.get('status', 'N/A')}")

        # exam_config.json
        exam_config_file = job_dir / "exam_config.json"
        print(f"   📄 exam_config.json: {exam_config_file.exists()}")
        if exam_config_file.exists():
            with open(exam_config_file, "r", encoding="utf-8") as f:
                config_data = json.load(f)
                print(f"      - exam_title: {config_data.get('exam_title', 'N/A')}")

        # answers目录
        answers_dir = job_dir / "answers"
        print(f"   📁 answers/: {answers_dir.exists()}")
        if answers_dir.exists():
            answer_files = list(answers_dir.glob("student_*.*"))
            print(f"      - 学生数: {len(answer_files)}")

        print()

    # 4. 测试 get_all_jobs 函数
    print("=" * 80)
    print("🧪 测试 get_all_jobs() 函数")
    print("=" * 80)
    print()

    jobs = get_all_jobs()
    print(f"📊 返回 {len(jobs)} 个任务:")
    print()

    for i, job in enumerate(jobs, 1):
        print(f"{i}. Job ID: {job.get('job_id', 'N/A')}")
        print(f"   考试标题: {job.get('exam_title', 'N/A')}")
        print(f"   学生数量: {job.get('student_count', 'N/A')}")
        print(f"   创建时间: {job.get('created_at', 'N/A')}")
        print(f"   状态: {job.get('status', 'N/A')}")
        print()

    # 5. 测试格式化函数
    print("=" * 80)
    print("🎨 测试任务名称格式化")
    print("=" * 80)
    print()

    from src.ui.app import format_job_display_name

    for i, job in enumerate(jobs, 1):
        display_name = format_job_display_name(job)
        print(f"{i}. {display_name}")

    print()
    print("=" * 80)
    print("✅ 检查完成")
    print("=" * 80)


if __name__ == "__main__":
    main()
