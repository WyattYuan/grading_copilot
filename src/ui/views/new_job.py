"""
新建评分任务页面
"""

import streamlit as st
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.ui.utils.api_client import create_grading_job, load_job_history


def show_new_job_page():
    """新建评分任务页面"""
    st.header("📤 新建评分任务")

    st.markdown(
        """
    ### 使用说明
    1. 上传考试配置JSON文件 (exam_config.json)
    2. 上传学生答案ZIP压缩包 (包含所有学生的答案文件)
    3. 点击"开始评分"按钮
    
    #### 学生答案文件格式要求:
    - 文件名: `student_XXX.txt`、`student_XXX.docx` 或 `student_XXX.md`
    - 内容格式:
    ```
    学生姓名: 张三
    学号: 1001
    性别: 男
    
    [作答: q1]
    这是第一题的答案
    
    [作答: q2]
    这是第二题的答案
    ```
    """
    )

    col1, col2 = st.columns(2)

    with col1:
        exam_config_file = st.file_uploader(
            "上传考试配置 (JSON)",
            type=["json"],
            help="包含题目、参考答案和评分标准的JSON文件",
            key="new_job_exam_config",
        )

        # 预览配置文件
        if exam_config_file is not None:
            try:
                config_content = json.loads(exam_config_file.getvalue().decode("utf-8"))
                with st.expander("👀 预览配置"):
                    st.json(config_content)
                    st.success(
                        f"✅ 配置有效：{config_content.get('exam_title', '未命名')}，{len(config_content.get('questions', []))} 道题"
                    )
            except json.JSONDecodeError:
                st.error("❌ JSON格式错误，请检查文件内容")
            except Exception as e:
                st.warning(f"⚠️ 预览失败: {str(e)}")

    with col2:
        student_answers_file = st.file_uploader(
            "上传学生答案 (ZIP)",
            type=["zip"],
            help="包含所有学生答案文件的ZIP压缩包",
            key="new_job_student_answers",
        )

        if student_answers_file:
            file_size = len(student_answers_file.getvalue())
            st.info(f"📦 文件大小: {file_size / 1024:.2f} KB")

    # 验证状态
    can_submit = exam_config_file is not None and student_answers_file is not None

    if not can_submit:
        missing = []
        if not exam_config_file:
            missing.append("考试配置")
        if not student_answers_file:
            missing.append("学生答案")
        st.warning(f"⚠️ 请上传: {', '.join(missing)}")

    if st.button(
        "🚀 开始评分",
        type="primary",
        disabled=not can_submit,
        key="new_job_submit_btn",
        use_container_width=True,
    ):
        with st.spinner("📤 正在提交任务..."):
            # 再次验证文件存在（类型检查）
            if exam_config_file is None or student_answers_file is None:
                st.error("❌ 请上传所有必需的文件")
                return

            result = create_grading_job(exam_config_file, student_answers_file)

            if result:
                job_id = result["job_id"]
                st.success(f"✅ 任务已创建! 任务ID: `{job_id}`")

                col1, col2 = st.columns(2)
                with col1:
                    st.info("💡 请前往「任务状态」页面查看进度")
                with col2:
                    if st.button("📊 立即查看状态", key="goto_status"):
                        st.session_state.current_job_id = job_id
                        st.session_state.active_tab = "status"
                        st.rerun()

                # 刷新任务列表
                st.cache_data.clear()
                st.session_state.app_jobs = load_job_history()
