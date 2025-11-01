"""
创建测试用例ZIP包
包含5名不同水平学生的作答
"""

import zipfile
from pathlib import Path


def create_test_zip():
    """创建测试用例ZIP包"""

    # 源文件目录
    examples_dir = Path("data/examples")

    # 学生答案文件
    student_files = [
        "student_2024001.txt",  # 优秀
        "student_2024002.txt",  # 良好
        "student_2024003.txt",  # 中等
        "student_2024004.txt",  # 及格
        "student_2024005.txt",  # 待提高
    ]

    # 创建ZIP文件
    zip_path = examples_dir / "test_student_answers.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for student_file in student_files:
            file_path = examples_dir / student_file
            if file_path.exists():
                zipf.write(file_path, student_file)
                print(f"✅ 已添加: {student_file}")
            else:
                print(f"❌ 文件不存在: {student_file}")

    print(f"\n📦 ZIP包已创建: {zip_path}")
    print(f"📊 包含 {len(student_files)} 名学生的作答")

    # 显示学生信息
    print("\n👥 学生名单:")
    students = [
        ("2024001", "张优秀", "优秀水平 - 答案完整、详细、有深度"),
        ("2024002", "李良好", "良好水平 - 答案正确、较完整"),
        ("2024003", "王中等", "中等水平 - 基本正确但不够详细"),
        ("2024004", "赵及格", "及格水平 - 回答简单、部分遗漏"),
        ("2024005", "孙待提高", "待提高 - 回答不完整、有错误"),
    ]

    for student_id, name, level in students:
        print(f"  - {student_id}: {name} ({level})")

    print("\n📝 考试配置文件: test_exam_config.json")
    print("   题目数量: 4题")
    print("   总分: 50分")
    print("   - q1: 列表和元组的区别 (10分)")
    print("   - q2: 偶数平方和函数 (15分)")
    print("   - q3: 装饰器原理 (12分)")
    print("   - q4: 斐波那契递归 (13分)")

    return zip_path


if __name__ == "__main__":
    create_test_zip()
