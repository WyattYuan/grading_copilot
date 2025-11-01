"""
测试文件计数逻辑
"""

from pathlib import Path
import sys

# 添加src到路径
sys.path.append(str(Path(__file__).parent.parent))

from src.config import config


def test_file_counting():
    """测试文件计数是否正确"""
    print("=" * 80)
    print("📊 测试学生答案文件计数")
    print("=" * 80)
    print()

    # 检查所有任务的answers目录
    uploads_dir = config.UPLOADS_DIR
    if not uploads_dir.exists():
        print("❌ uploads目录不存在")
        return

    job_dirs = [
        d for d in uploads_dir.iterdir() if d.is_dir() and d.name.startswith("job_")
    ]

    for job_dir in job_dirs:
        job_id = job_dir.name
        answers_dir = job_dir / "answers"

        if not answers_dir.exists():
            continue

        print(f"📁 任务: {job_id}")
        print(f"   目录: {answers_dir}")

        # 方法1: 旧方法（会重复计数）
        old_count = []
        for pattern in ["*.txt", "*.docx", "*.md"]:
            old_count.extend(answers_dir.glob(pattern))
            old_count.extend(answers_dir.glob(f"**/{pattern}"))

        # 方法2: 新方法（只搜索子目录）
        new_count = []
        for pattern in ["**/*.txt", "**/*.docx", "**/*.md"]:
            new_count.extend(answers_dir.glob(pattern))

        # 方法3: 新方法去重
        new_count_unique = list(set(new_count))

        # 方法4: 直接计数student_开头的文件
        student_files = list(answers_dir.glob("student_*.*"))

        print(f"   旧方法（有重复）: {len(old_count)} 个文件")
        print(f"   新方法（未去重）: {len(new_count)} 个文件")
        print(f"   新方法（已去重）: {len(new_count_unique)} 个文件")
        print(f"   student_*.*: {len(student_files)} 个文件")

        # 详细列出文件
        print(f"\n   文件列表:")
        for f in sorted(new_count_unique):
            print(f"      - {f.name}")

        # 检查是否有重复
        if len(old_count) != len(set(old_count)):
            print(f"\n   ⚠️  旧方法检测到重复文件！")
            print(f"      总数: {len(old_count)}, 去重后: {len(set(old_count))}")

        print()


if __name__ == "__main__":
    test_file_counting()
