"""
测试重构后的模块导入
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

print("✅ 测试开始...")
print(f"📁 项目路径: {project_root}")

try:
    print("\n1️⃣ 测试工具模块导入...")
    from src.ui.utils.api_client import check_api_connection, load_job_history
    from src.ui.utils.formatters import format_job_display_name, calculate_total_score

    print("   ✅ 工具模块导入成功")

    print("\n2️⃣ 测试组件模块导入...")
    from src.ui.components.sidebar import render_sidebar
    from src.ui.components.student_detail import show_student_detail

    print("   ✅ 组件模块导入成功")

    print("\n3️⃣ 测试页面模块导入...")
    from src.ui.views.exam_maker import show_exam_maker_page
    from src.ui.views.new_job import show_new_job_page
    from src.ui.views.job_status import show_job_status_page
    from src.ui.views.results import show_results_page
    from src.ui.views.adjustment import show_adjustment_page

    print("   ✅ 页面模块导入成功")

    print("\n4️⃣ 测试表单模块导入...")
    from src.ui.forms.question_forms import show_add_question_form

    print("   ✅ 表单模块导入成功")

    print("\n" + "=" * 50)
    print("🎉 所有模块导入测试通过！")
    print("=" * 50)

except ImportError as e:
    print(f"\n❌ 导入错误: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 其他错误: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
