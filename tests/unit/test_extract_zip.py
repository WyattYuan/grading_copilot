"""
测试 extract_zip 函数的文件计数
"""

from pathlib import Path
import sys
import tempfile
import zipfile

# 添加src到路径
sys.path.append(str(Path(__file__).parent.parent))

from src.api.file_utils import FileParser


def test_extract_zip():
    """测试extract_zip函数是否正确计数"""
    print("=" * 80)
    print("🧪 测试 extract_zip 函数")
    print("=" * 80)
    print()

    # 创建临时ZIP文件
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)

        # 创建5个测试文件
        test_files = []
        for i in range(1, 6):
            test_file = tmpdir_path / f"student_202400{i}.txt"
            test_file.write_text(f"Student {i} answer", encoding="utf-8")
            test_files.append(test_file)

        # 创建ZIP文件
        zip_path = tmpdir_path / "test_answers.zip"
        with zipfile.ZipFile(zip_path, "w") as zf:
            for f in test_files:
                zf.write(f, f.name)

        print(f"✅ 创建了 {len(test_files)} 个测试文件")
        print(f"✅ 创建了ZIP文件: {zip_path.name}")
        print()

        # 解压并计数
        extract_dir = tmpdir_path / "extracted"
        answer_files = FileParser.extract_zip(zip_path, extract_dir)

        print(f"📊 extract_zip 返回结果:")
        print(f"   文件数量: {len(answer_files)}")
        print(f"   文件列表:")
        for f in sorted(answer_files):
            print(f"      - {f.name}")
        print()

        # 验证
        expected_count = len(test_files)
        actual_count = len(answer_files)

        if actual_count == expected_count:
            print(f"✅ 测试通过！")
            print(f"   期望: {expected_count} 个文件")
            print(f"   实际: {actual_count} 个文件")
        else:
            print(f"❌ 测试失败！")
            print(f"   期望: {expected_count} 个文件")
            print(f"   实际: {actual_count} 个文件")
            print(f"   差异: {actual_count - expected_count}")

        print()
        print("=" * 80)


if __name__ == "__main__":
    test_extract_zip()
