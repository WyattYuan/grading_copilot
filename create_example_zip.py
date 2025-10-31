"""
创建示例数据的ZIP压缩包
"""

import zipfile
from pathlib import Path


def create_example_zip():
    """创建包含示例学生答案的ZIP文件"""
    examples_dir = Path(__file__).parent / "data" / "examples"
    zip_path = examples_dir / "student_answers.zip"

    # 查找所有学生答案文件
    answer_files = list(examples_dir.glob("student_*.txt"))

    if not answer_files:
        print("❌ 未找到学生答案文件")
        return

    # 创建ZIP文件
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for file in answer_files:
            zipf.write(file, file.name)
            print(f"✅ 已添加: {file.name}")

    print(f"\n🎉 ZIP文件创建成功: {zip_path}")
    print(f"📦 包含 {len(answer_files)} 个学生答案文件")


if __name__ == "__main__":
    create_example_zip()
