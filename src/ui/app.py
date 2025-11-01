"""
Streamlit 前端界面
"""

import streamlit as st
import requests
import pandas as pd
import time
from pathlib import Path
import sys

# 添加src到路径
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.config import config

# API基础URL
API_BASE_URL = f"http://{config.API_HOST}:{config.API_PORT}/api/v1"


def load_job_history():
    """从API加载任务历史"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["jobs"]
    except:
        return []


def main():
    """主界面"""
    st.set_page_config(page_title="AI智能评分系统", page_icon="📝", layout="wide")

    st.title("🎓 AI智能评分系统")

    # 初始化session_state - 加载任务历史
    if "jobs" not in st.session_state:
        st.session_state.jobs = load_job_history()

    # 侧边栏 - 显示任务历史和刷新按钮
    with st.sidebar:
        st.header("📋 任务历史")

        if st.button("🔄 刷新任务列表", use_container_width=True):
            st.session_state.jobs = load_job_history()
            st.rerun()

        if st.session_state.jobs:
            st.caption(f"共 {len(st.session_state.jobs)} 个任务")

            # 显示最近的5个任务
            for job in st.session_state.jobs[:5]:
                with st.expander(f"🔖 {job['job_id']}", expanded=False):
                    if job.get("exam_name"):
                        st.write(f"**考试名称:** {job['exam_name']}")
                    st.write(f"**学生数:** {job.get('student_count', 0)}")
                    if job.get("created_at"):
                        st.caption(f"创建时间: {job['created_at'][:19]}")
        else:
            st.info("暂无历史任务")

    # 使用标签页导航 - 更直观的页签式界面
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["📝 试卷制作", "📤 新建评分任务", "📊 任务状态", "📋 评分结果", "✏️ 人工微调"]
    )

    with tab1:
        show_exam_maker_page()

    with tab2:
        show_new_job_page()

    with tab3:
        show_job_status_page()

    with tab4:
        show_results_page()

    with tab5:
        show_adjustment_page()


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

    with col2:
        student_answers_file = st.file_uploader(
            "上传学生答案 (ZIP)",
            type=["zip"],
            help="包含所有学生答案文件的ZIP压缩包",
            key="new_job_student_answers",
        )

    if st.button(
        "🚀 开始评分",
        type="primary",
        disabled=not (exam_config_file and student_answers_file),
        key="new_job_submit_btn",
    ):
        with st.spinner("正在提交任务..."):
            if not exam_config_file or not student_answers_file:
                st.error("❌ 请上传所有必需的文件")
                return
            try:
                # 准备文件
                files = {
                    "exam_config": (
                        "exam_config.json",
                        exam_config_file.getvalue(),
                        "application/json",
                    ),
                    "student_answers": (
                        "student_answers.zip",
                        student_answers_file.getvalue(),
                        "application/zip",
                    ),
                }

                # 调用API
                response = requests.post(f"{API_BASE_URL}/jobs/start", files=files)
                response.raise_for_status()

                result = response.json()
                job_id = result["job_id"]

                st.success(f"✅ 任务已创建! 任务ID: `{job_id}`")
                st.info("请前往「查看任务状态」页面查看进度")

                # 刷新任务列表
                st.session_state.jobs = load_job_history()
                st.session_state.current_job_id = job_id

            except Exception as e:
                st.error(f"❌ 任务创建失败: {str(e)}")


def show_job_status_page():
    """查看任务状态页面"""
    st.header("📊 任务状态监控")

    # 选择历史任务
    job_id = None
    if st.session_state.jobs:
        job_options = [""] + [job["job_id"] for job in st.session_state.jobs]
        selected_job = st.selectbox(
            "选择任务",
            job_options,
            format_func=lambda x: "请选择任务..." if x == "" else x,
            key="status_history_select",
        )
        if selected_job:
            job_id = selected_job
    else:
        st.info("💡 暂无历史任务，请先创建评分任务")
        return

    if job_id:
        # 自动刷新按钮
        col1, col2 = st.columns([1, 4])
        with col1:
            auto_refresh = st.checkbox(
                "自动刷新", value=False, key="status_auto_refresh"
            )
        with col2:
            if st.button("🔄 手动刷新", key="status_manual_refresh"):
                st.rerun()

        try:
            # 获取任务状态
            response = requests.get(f"{API_BASE_URL}/jobs/{job_id}/status")
            response.raise_for_status()

            status_data = response.json()

            # 显示状态
            st.subheader(f"任务 {job_id}")

            col1, col2, col3 = st.columns(3)

            with col1:
                status = status_data["status"]
                status_emoji = {
                    "pending": "⏳",
                    "running": "🔄",
                    "completed": "✅",
                    "failed": "❌",
                }
                st.metric("状态", f"{status_emoji.get(status, '')} {status}")

            with col2:
                processed = status_data["processed_questions"]
                total = status_data["total_questions"]
                st.metric("进度", f"{processed}/{total}")

            with col3:
                if total > 0:
                    progress = processed / total
                    st.metric("完成率", f"{progress * 100:.1f}%")

            # 进度条
            if total > 0:
                st.progress(processed / total)

            # 时间信息
            st.markdown(
                f"""
            - **创建时间:** {status_data['created_at']}
            - **更新时间:** {status_data['updated_at']}
            """
            )

            # 如果失败,显示错误信息
            if status == "failed" and status_data.get("error_message"):
                st.error(f"错误信息: {status_data['error_message']}")

            # 如果完成,显示跳转按钮
            if status == "completed":
                st.success("🎉 评分完成!")
                if st.button("查看评分结果 →", key="status_view_results_btn"):
                    st.session_state.current_job_id = job_id
                    st.rerun()

            # 自动刷新
            if auto_refresh and status in ["pending", "running"]:
                time.sleep(2)
                st.rerun()

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                st.error("❌ 任务不存在")
            else:
                st.error(f"❌ 获取任务状态失败: {str(e)}")
        except Exception as e:
            st.error(f"❌ 发生错误: {str(e)}")


def show_results_page():
    """查看评分结果页面"""
    st.header("📈 评分结果")

    # 选择历史任务
    job_id = st.session_state.get("current_job_id", "")

    if st.session_state.jobs:
        # 如果有current_job_id且在列表中，设置为默认值
        default_index = 0
        if job_id:
            job_ids = [job["job_id"] for job in st.session_state.jobs]
            if job_id in job_ids:
                default_index = job_ids.index(job_id) + 1  # +1因为第一个是空选项

        job_options = [""] + [job["job_id"] for job in st.session_state.jobs]
        selected_job = st.selectbox(
            "选择任务",
            job_options,
            index=default_index,
            format_func=lambda x: "请选择任务..." if x == "" else x,
            key="results_history_select",
        )
        if selected_job:
            job_id = selected_job
            st.session_state.current_job_id = job_id
    else:
        st.info("💡 暂无历史任务，请先创建评分任务")
        return

    if job_id:
        try:
            # 获取总分表
            response = requests.get(f"{API_BASE_URL}/jobs/{job_id}/summary")
            response.raise_for_status()

            summary_data = response.json()
            df = pd.DataFrame(summary_data["data"])

            # 显示统计信息
            st.subheader("📊 总体统计")
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("学生总数", len(df))

            with col2:
                avg_score = df["total_score"].mean()
                st.metric("平均分", f"{avg_score:.2f}")

            with col3:
                max_score = df["total_score"].max()
                st.metric("最高分", f"{max_score:.2f}")

            with col4:
                min_score = df["total_score"].min()
                st.metric("最低分", f"{min_score:.2f}")

            # 显示总分表
            st.subheader("📋 总分表")
            st.dataframe(df, use_container_width=True, hide_index=True)

            # 下载按钮
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 下载CSV",
                data=csv,
                file_name=f"{job_id}_summary.csv",
                mime="text/csv",
                key="results_download_csv",
            )

            # 选择学生查看详情
            st.subheader("🔍 查看学生详情")
            selected_student = st.selectbox(
                "选择学生",
                df["student_id"].tolist(),
                index=None,
                key="results_student_select",
            )

            if selected_student:
                show_student_detail(job_id, selected_student)

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                st.error("❌ 任务不存在")
            elif e.response.status_code == 400:
                st.warning("⏳ 任务尚未完成,请稍后查看")
            else:
                st.error(f"❌ 获取结果失败: {str(e)}")
        except Exception as e:
            st.error(f"❌ 发生错误: {str(e)}")


def show_student_detail(job_id: str, student_id: str):
    """显示学生详情"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}/students/{student_id}")
        response.raise_for_status()

        data = response.json()

        st.markdown(f"### 学生信息")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("姓名", data.get("student_name", "未知"))
        with col2:
            st.metric("学号", student_id)
        with col3:
            st.metric("性别", data.get("student_gender", "未知"))

        st.metric("总分", f"{data['total_score']:.2f}")

        for q in data["questions"]:
            with st.expander(
                f"📝 {q['question_id']} - {q['final_score']:.1f}/{q['max_score']:.1f}分"
            ):
                st.markdown(f"**题目:** {q['question_description']}")
                st.markdown(f"**学生答案:**")
                st.info(q["student_answer"])

                st.markdown(f"**AI评分:** {q['ai_score']:.1f}分")
                st.markdown(f"**AI评分依据:**")
                st.write(q["ai_rationale"])

                if q["human_override_rationale"]:
                    st.markdown(f"**人工调整:** {q['final_score']:.1f}分")
                    st.markdown(f"**调整理由:**")
                    st.warning(q["human_override_rationale"])

                st.caption(f"最后修改者: {q['last_modified_by']}")

    except Exception as e:
        st.error(f"获取学生详情失败: {str(e)}")


def show_adjustment_page():
    """人工微调页面"""
    st.header("✏️ 人工微调")

    st.markdown(
        """
    在此页面,您可以审查AI的评分结果并进行微调。
    修改后的分数会自动同步到总分表。
    """
    )

    # 选择历史任务
    job_id = None
    if st.session_state.jobs:
        job_options = [""] + [job["job_id"] for job in st.session_state.jobs]
        selected_job = st.selectbox(
            "选择任务",
            job_options,
            format_func=lambda x: "请选择任务..." if x == "" else x,
            key="adjustment_history_select",
        )
        if selected_job:
            job_id = selected_job
    else:
        st.info("💡 暂无历史任务，请先创建评分任务")
        return

    if not job_id:
        st.info("👆 请先选择一个任务")
        return

    try:
        # 获取该任务的所有报告
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}/summary")
        response.raise_for_status()

        summary_data = response.json()
        student_ids = [item["student_id"] for item in summary_data["data"]]

        if not student_ids:
            st.warning("⚠️ 该任务暂无评分报告")
            return

        # 使用selectbox选择学生
        selected_student = st.selectbox(
            "选择学生",
            student_ids,
            format_func=lambda x: f"学生 {x}",
            key="adjustment_student_select",
        )

        if selected_student:
            st.markdown("---")
            show_student_reports_for_adjustment(job_id, selected_student)

    except Exception as e:
        st.error(f"❌ 加载报告失败: {str(e)}")


def show_student_reports_for_adjustment(job_id: str, student_id: str):
    """显示单个学生的所有报告,支持逐题微调"""

    try:
        # 获取学生的所有报告
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}/students/{student_id}")
        response.raise_for_status()

        data = response.json()

        st.subheader(f"📝 学生评分报告")

        # 显示学生信息
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("姓名", data.get("student_name", "未知"))
        with col2:
            st.metric("学号", student_id)
        with col3:
            st.metric("性别", data.get("student_gender", "未知"))

        # 显示总分
        col1, col2 = st.columns(2)
        with col1:
            st.metric("当前总分", f"{data['total_score']:.1f}")
        with col2:
            max_total = sum(q["max_score"] for q in data["questions"])
            st.metric("满分", f"{max_total:.1f}")

        st.markdown("---")

        # 逐题展示
        for idx, q in enumerate(data["questions"], 1):
            with st.expander(
                f"📝 题目 {q['question_id']} - {q['final_score']:.1f}/{q['max_score']:.1f}分",
                expanded=(idx == 1),  # 默认展开第一题
            ):
                # 题目信息
                st.markdown(f"**题目描述:** {q['question_description']}")

                st.markdown("---")

                # 学生答案
                st.markdown("**学生答案:**")
                st.info(q["student_answer"])

                st.markdown("---")

                # AI评分信息
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("AI给分", f"{q['ai_score']:.1f}")
                with col2:
                    st.metric("当前生效分数", f"{q['final_score']:.1f}")

                st.markdown("**AI评分依据:**")
                st.write(q["ai_rationale"])

                if q["human_override_rationale"]:
                    st.markdown("**人工调整说明:**")
                    st.warning(q["human_override_rationale"])
                    st.caption(f"修改者: {q['last_modified_by']}")

                st.markdown("---")

                # 修改按钮
                unique_key = f"edit_{job_id}_{student_id}_{q['question_id']}"

                if st.button(
                    f"✏️ 修改此题评分", key=f"btn_{unique_key}", type="secondary"
                ):
                    st.session_state[f"editing_{unique_key}"] = True

                # 如果点击了修改按钮,显示修改表单
                if st.session_state.get(f"editing_{unique_key}", False):
                    st.markdown("#### 📝 修改评分")

                    with st.form(key=f"form_{unique_key}"):
                        new_score = st.number_input(
                            "新分数",
                            min_value=0.0,
                            max_value=float(q["max_score"]),
                            value=float(q["final_score"]),
                            step=0.5,
                            key=f"score_{unique_key}",
                        )

                        new_rationale = st.text_area(
                            "调整理由",
                            value=q["human_override_rationale"] or "",
                            placeholder="请说明为什么要调整分数...",
                            key=f"rationale_{unique_key}",
                        )

                        modified_by = st.text_input(
                            "修改者姓名",
                            value="Teacher",
                            placeholder="请输入您的姓名",
                            key=f"modifier_{unique_key}",
                        )

                        col1, col2 = st.columns([1, 1])

                        with col1:
                            submitted = st.form_submit_button(
                                "💾 提交修改", type="primary"
                            )

                        with col2:
                            cancelled = st.form_submit_button("❌ 取消")

                        if cancelled:
                            st.session_state[f"editing_{unique_key}"] = False
                            st.rerun()

                        if submitted:
                            try:
                                # 提交更新
                                update_data = {
                                    "new_score": new_score,
                                    "new_rationale": new_rationale,
                                    "modified_by": modified_by,
                                }

                                response = requests.put(
                                    f"{API_BASE_URL}/jobs/{job_id}/reports/{student_id}/{q['question_id']}",
                                    json=update_data,
                                )
                                response.raise_for_status()

                                st.success("✅ 修改成功! 总分表已自动同步")

                                # 清除编辑状态
                                st.session_state[f"editing_{unique_key}"] = False

                                # 等待一秒后刷新
                                time.sleep(1)
                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ 提交失败: {str(e)}")

    except Exception as e:
        st.error(f"❌ 获取学生详情失败: {str(e)}")


def calculate_total_score(questions_data: list) -> float:
    """计算试卷总分"""
    total = 0.0
    for q in questions_data:
        if q.get("is_composite", False):
            # 大题：累加所有小题分数
            total += sum(sq["max_score"] for sq in q.get("sub_questions", []))
        else:
            # 单题
            total += q.get("max_score", 0.0)
    return total


def import_exam_config(uploaded_file):
    """从JSON文件导入试卷配置"""
    import json

    try:
        content = uploaded_file.read().decode("utf-8")
        data = json.loads(content)

        if "exam_title" in data:
            st.session_state.exam_title = data["exam_title"]

        if "questions" in data:
            st.session_state.questions_data = data["questions"]
            st.success(
                f"✅ 成功导入试卷：{data.get('exam_title', '未命名')}，共 {len(data['questions'])} 题"
            )
            # 不需要 st.rerun()，让页面自然更新
    except Exception as e:
        st.error(f"❌ 导入失败: {str(e)}")


def show_exam_maker_page():
    """试卷制作页面"""
    st.header("📝 试卷制作工具")

    st.markdown(
        """
    在此页面可以可视化地创建试卷，支持：
    - 📄 **单题**：普通题目
    - 📚 **大题+小题**：一道大题包含多道小题
    - 📥 **导出配置**：生成 exam_config.json
    - 📋 **导出模板**：生成学生作答 Markdown 模板
    """
    )

    st.markdown("---")

    # 初始化session state
    if "exam_title" not in st.session_state:
        st.session_state.exam_title = "期中考试"
    if "questions_data" not in st.session_state:
        st.session_state.questions_data = []

    # 顶部工具栏
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        exam_title = st.text_input(
            "📋 试卷标题", value=st.session_state.exam_title, key="exam_title_input"
        )
        st.session_state.exam_title = exam_title

    with col2:
        # 计算试卷总分
        total_score = calculate_total_score(st.session_state.questions_data)
        st.metric("📊 试卷总分", f"{total_score} 分")

    with col3:
        st.metric("📚 题目数量", f"{len(st.session_state.questions_data)} 题")

    st.markdown("---")

    # 导入功能
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ 添加单题", use_container_width=True, type="primary"):
            st.session_state.adding_question_type = "single"
            st.rerun()

    with col2:
        if st.button(
            "➕ 添加大题（含小题）", use_container_width=True, type="secondary"
        ):
            st.session_state.adding_question_type = "composite"
            # 初始化大题编辑器状态 - 确保所有字段都存在
            st.session_state.composite_temp = {
                "id": "",
                "type": "text",
                "description": "",
                "sub_questions": [],
            }
            st.rerun()

    with col3:
        uploaded_json = st.file_uploader(
            "📂 导入已有JSON", type=["json"], key="import_json"
        )
        if uploaded_json:
            import_exam_config(uploaded_json)

    # 显示添加题目表单
    if st.session_state.get("adding_question_type"):
        show_add_question_form(st.session_state.adding_question_type)

    st.markdown("---")

    # 显示已添加的题目列表
    st.subheader(f"📚 题目列表")

    if st.session_state.questions_data:
        show_questions_list()
    else:
        st.info("还没有添加题目，请点击上方按钮添加")

    st.markdown("---")

    # 导出功能
    if st.session_state.questions_data:
        st.subheader("📥 导出")
        show_export_section()


def show_add_question_form(question_type: str):
    """显示添加题目的表单"""

    if question_type == "single":
        show_add_single_question_form()
    else:
        show_add_composite_question_form()


def show_add_single_question_form():
    """添加单题表单 - 分步式设计"""
    st.markdown("### ✏️ 添加单题")

    # 初始化临时数据
    if "single_temp" not in st.session_state:
        st.session_state.single_temp = {
            "id": "",
            "type": "text",
            "description": "",
            "max_score": 10.0,
            "reference_answer": "",
            "scoring_criteria": [],
        }

    temp = st.session_state.single_temp

    # 第一部分：基本信息
    st.markdown("---")
    st.markdown(
        """
        <div style="background-color: #e3f2fd; padding: 10px; border-radius: 8px; border-left: 4px solid #2196f3;">
            <h4 style="margin: 0; color: #2196f3;">📋 第一步：填写题目基本信息</h4>
        </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            temp["id"] = st.text_input(
                "题目ID *", value=temp["id"], placeholder="例如: q1", key="single_id"
            )
            temp["type"] = st.selectbox(
                "题目类型",
                ["text", "code", "multimodal"],
                index=["text", "code", "multimodal"].index(temp["type"]),
                key="single_type",
            )
        with col2:
            temp["max_score"] = st.number_input(
                "满分 *",
                min_value=0.0,
                value=temp["max_score"],
                step=0.5,
                key="single_score",
            )

        temp["description"] = st.text_area(
            "题目描述 *",
            value=temp["description"],
            placeholder="输入题目内容...",
            height=100,
            key="single_desc",
        )
        temp["reference_answer"] = st.text_area(
            "参考答案 *",
            value=temp["reference_answer"],
            placeholder="输入参考答案...",
            height=80,
            key="single_answer",
        )

    st.markdown("---")

    # 第二部分：评分标准管理
    st.markdown(
        """
        <div style="background-color: #fff3e0; padding: 10px; border-radius: 8px; border-left: 4px solid #ff9800;">
            <h4 style="margin: 0; color: #ff9800;">📊 第二步：添加评分标准</h4>
        </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("")

    with st.container(border=True):
        col1, col2 = st.columns([2, 2])
        with col1:
            if st.button("➕ 添加评分标准", use_container_width=True):
                st.session_state.adding_single_criterion = True
        with col2:
            criteria_count = len(temp["scoring_criteria"])
        total_criteria_points = sum(c["points"] for c in temp["scoring_criteria"])
        st.info(f"已添加 {criteria_count} 项标准，共 {total_criteria_points} 分")

    # 添加评分标准的表单
    if st.session_state.get("adding_single_criterion", False):
        with st.container():
            st.markdown("##### ➕ 新增评分标准")
            with st.form(key="add_single_criterion_form"):
                col1, col2 = st.columns([1, 3])
                with col1:
                    criterion_points = st.number_input(
                        "分数 *", min_value=0.0, value=2.0, step=0.5
                    )
                with col2:
                    criterion_desc = st.text_input(
                        "标准描述 *", placeholder="例如：正确说明概念定义"
                    )

                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button(
                        "✅ 确认添加", type="primary", use_container_width=True
                    )
                with col2:
                    cancelled = st.form_submit_button(
                        "❌ 取消", use_container_width=True
                    )

                if cancelled:
                    st.session_state.adding_single_criterion = False
                    st.rerun()

                if submitted:
                    if not criterion_desc:
                        st.error("请填写标准描述")
                    else:
                        temp["scoring_criteria"].append(
                            {"points": criterion_points, "criterion": criterion_desc}
                        )
                        st.session_state.adding_single_criterion = False
                        st.success(f"✅ 已添加评分标准")
                        time.sleep(0.3)
                        st.rerun()

        # 显示已添加的评分标准
        if temp["scoring_criteria"]:
            st.markdown("")
            st.markdown("**📝 已添加的评分标准：**")
            for idx, criterion in enumerate(temp["scoring_criteria"]):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(
                        f"{idx+1}. **{criterion['points']}分** - {criterion['criterion']}"
                    )
                with col2:
                    if st.button("🗑️", key=f"del_single_criterion_{idx}", help="删除"):
                        temp["scoring_criteria"].pop(idx)
                        st.rerun()

    st.markdown("---")

    # 第三步：完成
    st.markdown(
        """
        <div style="background-color: #e8f5e9; padding: 10px; border-radius: 8px; border-left: 4px solid #4caf50;">
            <h4 style="margin: 0; color: #4caf50;">✅ 第三步：完成添加</h4>
        </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 完成并添加题目", type="primary", use_container_width=True):
                if (
                    not temp["id"]
                    or not temp["description"]
                    or not temp["reference_answer"]
                ):
                    st.error("请填写所有必填字段（标记*）")
                elif not temp["scoring_criteria"]:
                    st.error("请至少添加一项评分标准")
                else:
                    # 添加到题目列表
                    st.session_state.questions_data.append(
                        {
                            "id": temp["id"],
                            "type": temp["type"],
                            "description": temp["description"],
                            "max_score": temp["max_score"],
                            "reference_answer": temp["reference_answer"],
                            "scoring_criteria": temp["scoring_criteria"],
                            "is_composite": False,
                        }
                    )
                    # 清理临时数据
                    del st.session_state.single_temp
                    del st.session_state.adding_question_type
                    if "adding_single_criterion" in st.session_state:
                        del st.session_state.adding_single_criterion
                    st.success(f"✅ 已添加题目: {temp['id']}")
                    time.sleep(0.5)
                    st.rerun()

        with col2:
            if st.button("❌ 取消", use_container_width=True):
                # 清理临时数据
                del st.session_state.single_temp
                del st.session_state.adding_question_type
                if "adding_single_criterion" in st.session_state:
                    del st.session_state.adding_single_criterion
                st.rerun()


def show_add_composite_question_form():
    """添加大题表单 - 分步式设计"""
    st.markdown("### ✏️ 添加大题（含小题）")

    # 初始化临时数据 - 确保所有必要字段都存在
    if "composite_temp" not in st.session_state:
        st.session_state.composite_temp = {
            "id": "",
            "type": "text",
            "description": "",
            "sub_questions": [],
        }

    # 确保现有的 composite_temp 包含所有必要字段
    temp = st.session_state.composite_temp
    if "id" not in temp:
        temp["id"] = ""
    if "type" not in temp:
        temp["type"] = "text"
    if "description" not in temp:
        temp["description"] = ""
    if "sub_questions" not in temp:
        temp["sub_questions"] = []

    # ========== 第一部分：大题基本信息 ==========
    st.markdown("---")
    st.markdown(
        """
        <div style="background-color: #e8f4f8; padding: 10px; border-radius: 8px; border-left: 4px solid #1f77b4;">
            <h3 style="margin: 0; color: #1f77b4;">📋 第一步：大题基本信息</h3>
        </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("")
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            temp["id"] = st.text_input(
                "大题ID *", value=temp["id"], placeholder="例如: q1", key="composite_id"
            )
        with col2:
            temp["type"] = st.selectbox(
                "题目类型",
                ["text", "code", "multimodal"],
                index=["text", "code", "multimodal"].index(temp["type"]),
                key="composite_type",
            )

        temp["description"] = st.text_area(
            "大题描述 *",
            value=temp["description"],
            placeholder="输入大题总述...",
            height=80,
            key="composite_desc",
        )

    # ========== 第二部分：小题管理 ==========
    st.markdown("---")
    st.markdown(
        """
        <div style="background-color: #fff4e6; padding: 10px; border-radius: 8px; border-left: 4px solid #ff9800;">
            <h3 style="margin: 0; color: #ff9800;">📚 第二步：管理小题</h3>
        </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("")

    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            if st.button("➕ 添加小题", use_container_width=True):
                st.session_state.adding_subquestion = True
        with col2:
            subq_count = len(temp["sub_questions"])
            total_subq_score = sum(sq["max_score"] for sq in temp["sub_questions"])
            st.info(f"已添加 {subq_count} 道小题，共 {total_subq_score} 分")
        with col3:
            pass

    # 添加小题的界面 - 分步式
    if st.session_state.get("adding_subquestion", False):
        # 初始化当前正在编辑的小题
        if "current_subquestion" not in st.session_state:
            subq_index = len(temp["sub_questions"]) + 1
            st.session_state.current_subquestion = {
                "id": (
                    f"{temp['id']}_{subq_index}" if temp["id"] else f"sub_{subq_index}"
                ),
                "description": "",
                "max_score": 5.0,
                "reference_answer": "",
                "scoring_criteria": [],
            }

        curr_subq = st.session_state.current_subquestion

        # 使用明显的视觉容器区分小题编辑区
        st.markdown("---")
        st.markdown(
            """
            <div style="background-color: #f3e5f5; padding: 12px; border-radius: 8px; border-left: 4px solid #9c27b0;">
                <h4 style="margin: 0; color: #9c27b0;">🔧 正在编辑小题</h4>
            </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown("")
        with st.container(border=True):
            st.markdown("##### ➕ 新增小题")

            # 步骤A：填写基本信息
            st.markdown(
                """
                <div style="background-color: #f1f8e9; padding: 8px; border-radius: 5px; margin-bottom: 10px;">
                    <h6 style="margin: 0; color: #558b2f;">🔹 步骤A：填写小题基本信息</h6>
                </div>
            """,
                unsafe_allow_html=True,
            )
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    curr_subq["id"] = st.text_input(
                        "小题ID *", value=curr_subq["id"], key="current_subq_id"
                    )
                    curr_subq["max_score"] = st.number_input(
                        "满分 *",
                        min_value=0.0,
                        value=curr_subq["max_score"],
                        step=0.5,
                        key="current_subq_score",
                    )
                with col2:
                    curr_subq["description"] = st.text_area(
                        "小题描述 *",
                        value=curr_subq["description"],
                        placeholder="小题内容...",
                        height=60,
                        key="current_subq_desc",
                    )
                    curr_subq["reference_answer"] = st.text_area(
                        "参考答案 *",
                        value=curr_subq["reference_answer"],
                        placeholder="参考答案...",
                        height=60,
                        key="current_subq_answer",
                    )

            st.markdown("")  # 空行分隔

            # 步骤B：添加评分标准
            st.markdown(
                """
                <div style="background-color: #fff3e0; padding: 8px; border-radius: 5px; margin-bottom: 10px;">
                    <h6 style="margin: 0; color: #ef6c00;">🔹 步骤B：添加评分标准</h6>
                </div>
            """,
                unsafe_allow_html=True,
            )
            with st.container(border=True):
                col1, col2 = st.columns([2, 2])
                with col1:
                    if st.button(
                        "➕ 添加评分标准",
                        key="add_subq_criterion_btn",
                        use_container_width=True,
                    ):
                        st.session_state.adding_subq_criterion = True
                with col2:
                    criteria_count = len(curr_subq["scoring_criteria"])
                    total_points = sum(
                        c["points"] for c in curr_subq["scoring_criteria"]
                    )
                    st.info(f"已添加 {criteria_count} 项，共 {total_points} 分")

                # 添加评分标准的表单
                if st.session_state.get("adding_subq_criterion", False):
                    with st.form(key="add_subq_criterion_form"):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            criterion_points = st.number_input(
                                "分数 *", min_value=0.0, value=2.0, step=0.5
                            )
                        with col2:
                            criterion_desc = st.text_input(
                                "标准描述 *", placeholder="例如：正确列举要点"
                            )

                        col1, col2 = st.columns(2)
                        with col1:
                            submitted = st.form_submit_button(
                                "✅ 确认添加", type="primary", use_container_width=True
                            )
                        with col2:
                            cancelled = st.form_submit_button(
                                "❌ 取消", use_container_width=True
                            )

                        if cancelled:
                            st.session_state.adding_subq_criterion = False
                            st.rerun()

                        if submitted:
                            if not criterion_desc:
                                st.error("请填写标准描述")
                            else:
                                curr_subq["scoring_criteria"].append(
                                    {
                                        "points": criterion_points,
                                        "criterion": criterion_desc,
                                    }
                                )
                                st.session_state.adding_subq_criterion = False
                                st.success(f"✅ 已添加评分标准")
                                time.sleep(0.3)
                                st.rerun()

                # 显示已添加的评分标准
                if curr_subq["scoring_criteria"]:
                    st.markdown("")
                    st.markdown("**已添加的评分标准：**")
                    for idx, criterion in enumerate(curr_subq["scoring_criteria"]):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(
                                f"{idx+1}. **{criterion['points']}分** - {criterion['criterion']}"
                            )
                        with col2:
                            if st.button(
                                "🗑️", key=f"del_subq_criterion_{idx}", help="删除"
                            ):
                                curr_subq["scoring_criteria"].pop(idx)
                                st.rerun()

            st.markdown("")  # 空行分隔

            # 步骤C：完成小题
            st.markdown(
                """
                <div style="background-color: #e8f5e9; padding: 8px; border-radius: 5px; margin-bottom: 10px;">
                    <h6 style="margin: 0; color: #2e7d32;">🔹 步骤C：完成小题</h6>
                </div>
            """,
                unsafe_allow_html=True,
            )
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "✅ 完成并添加小题",
                    type="primary",
                    use_container_width=True,
                    key="finish_subq_btn",
                ):
                    if (
                        not curr_subq["id"]
                        or not curr_subq["description"]
                        or not curr_subq["reference_answer"]
                    ):
                        st.error("请填写所有必填字段")
                    elif not curr_subq["scoring_criteria"]:
                        st.error("请至少添加一项评分标准")
                    else:
                        temp["sub_questions"].append(
                            {
                                "id": curr_subq["id"],
                                "description": curr_subq["description"],
                                "max_score": curr_subq["max_score"],
                                "reference_answer": curr_subq["reference_answer"],
                                "scoring_criteria": curr_subq["scoring_criteria"],
                            }
                        )
                        # 清理临时数据
                        del st.session_state.current_subquestion
                        st.session_state.adding_subquestion = False
                        if "adding_subq_criterion" in st.session_state:
                            del st.session_state.adding_subq_criterion
                        st.success(f"✅ 已添加小题: {curr_subq['id']}")
                        time.sleep(0.3)
                        st.rerun()
            with col2:
                if st.button(
                    "❌ 取消", use_container_width=True, key="cancel_subq_btn"
                ):
                    del st.session_state.current_subquestion
                    st.session_state.adding_subquestion = False
                    if "adding_subq_criterion" in st.session_state:
                        del st.session_state.adding_subq_criterion
                    st.rerun()

    # 显示已添加的小题
    if temp["sub_questions"]:
        st.markdown("")
        st.markdown("##### 📝 已添加的小题")
        with st.container(border=True):
            for idx, sq in enumerate(temp["sub_questions"]):
                with st.expander(f"小题 {idx+1}: {sq['id']} ({sq['max_score']}分)"):
                    st.write(f"**描述:** {sq['description']}")
                    st.write(f"**参考答案:** {sq['reference_answer']}")
                    st.write("**评分标准:**")
                    for c in sq["scoring_criteria"]:
                        st.write(f"  - {c['points']}分: {c['criterion']}")

                    if st.button(f"🗑️ 删除此小题", key=f"del_subq_{idx}"):
                        temp["sub_questions"].pop(idx)
                        st.rerun()

    # ========== 第三步：完成大题 ==========
    st.markdown("---")
    st.markdown(
        """
        <div style="background-color: #e8f5e9; padding: 10px; border-radius: 8px; border-left: 4px solid #4caf50;">
            <h3 style="margin: 0; color: #4caf50;">✅ 第三步：完成添加大题</h3>
        </div>
    """,
        unsafe_allow_html=True,
    )
    st.markdown("")

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ 完成并添加大题", type="primary", use_container_width=True):
                if not temp["id"] or not temp["description"]:
                    st.error("请填写大题ID和描述")
                elif not temp["sub_questions"]:
                    st.error("请至少添加一道小题")
                else:
                    # 添加到题目列表
                    st.session_state.questions_data.append(
                        {
                            "id": temp["id"],
                            "type": temp["type"],
                            "description": temp["description"],
                            "sub_questions": temp["sub_questions"],
                            "is_composite": True,
                        }
                    )
                    # 清理临时数据
                    del st.session_state.composite_temp
                    del st.session_state.adding_question_type
                    if "adding_subquestion" in st.session_state:
                        del st.session_state.adding_subquestion
                    st.success(
                        f"✅ 已添加大题: {temp['id']} (含 {len(temp['sub_questions'])} 道小题)"
                    )
                    time.sleep(0.5)
                    st.rerun()

        with col2:
            if st.button("❌ 取消", use_container_width=True):
                # 清理临时数据
                del st.session_state.composite_temp
                del st.session_state.adding_question_type
                if "adding_subquestion" in st.session_state:
                    del st.session_state.adding_subquestion
                st.rerun()


def show_questions_list():
    """显示题目列表 - 支持排序"""
    for idx, q in enumerate(st.session_state.questions_data):
        is_composite = q.get("is_composite", False)

        # 题目卡片容器
        container = st.container()
        with container:
            col_info, col_btns = st.columns([5, 1])

            with col_info:
                if is_composite:
                    # 大题
                    total_score = sum(
                        sq["max_score"] for sq in q.get("sub_questions", [])
                    )
                    with st.expander(
                        f"📚 {idx+1}. {q['id']} - {q['description'][:40]}... (大题，共{total_score}分)",
                        expanded=False,
                    ):
                        st.write(f"**题目类型:** {q['type']}")
                        st.write(f"**小题数:** {len(q.get('sub_questions', []))}")

                        # 显示大题描述
                        st.markdown("---")
                        st.markdown("**📋 大题描述:**")
                        st.info(q["description"])

                        st.markdown("---")
                        st.markdown("**📚 小题列表:**")

                        for sq_idx, sq in enumerate(q.get("sub_questions", []), 1):
                            st.markdown(
                                f"##### 小题 {sq_idx}: {sq['id']} ({sq['max_score']}分)"
                            )
                            st.write(f"**描述:** {sq['description']}")
                            st.write(f"**参考答案:** {sq['reference_answer']}")
                            st.write("**评分标准:**")
                            for c in sq["scoring_criteria"]:
                                st.write(f"  - {c['points']}分: {c['criterion']}")
                            if sq_idx < len(q.get("sub_questions", [])):
                                st.markdown("---")
                else:
                    # 单题
                    with st.expander(
                        f"📄 {idx+1}. {q['id']} - {q['description'][:40]}... ({q['max_score']}分)",
                        expanded=False,
                    ):
                        st.write(f"**题目类型:** {q['type']}")
                        st.write(f"**满分:** {q['max_score']}")
                        st.write(f"**题目描述:** {q['description']}")
                        st.write(f"**参考答案:** {q['reference_answer']}")
                        st.write("**评分标准:**")
                        for c in q["scoring_criteria"]:
                            st.write(f"  - {c['points']}分: {c['criterion']}")

            with col_btns:
                # 排序和删除按钮
                if idx > 0:
                    if st.button("⬆️", key=f"up_{idx}", help="上移"):
                        (
                            st.session_state.questions_data[idx],
                            st.session_state.questions_data[idx - 1],
                        ) = (
                            st.session_state.questions_data[idx - 1],
                            st.session_state.questions_data[idx],
                        )
                        st.rerun()

                if idx < len(st.session_state.questions_data) - 1:
                    if st.button("⬇️", key=f"down_{idx}", help="下移"):
                        (
                            st.session_state.questions_data[idx],
                            st.session_state.questions_data[idx + 1],
                        ) = (
                            st.session_state.questions_data[idx + 1],
                            st.session_state.questions_data[idx],
                        )
                        st.rerun()

                if st.button("🗑️", key=f"del_q_{idx}", help="删除"):
                    st.session_state.questions_data.pop(idx)
                    st.rerun()


def show_export_section():
    """导出功能区域"""
    import json

    col1, col2 = st.columns(2)

    with col1:
        if st.button(
            "📥 导出试卷配置 (JSON)", use_container_width=True, type="primary"
        ):
            # 生成 exam_config.json
            exam_config = {
                "exam_title": st.session_state.exam_title,
                "questions": st.session_state.questions_data,
            }

            json_str = json.dumps(exam_config, ensure_ascii=False, indent=2)
            filename = f"exam_config_{st.session_state.exam_title}.json"

            st.download_button(
                label="⬇️ 下载 JSON 文件",
                data=json_str,
                file_name=filename,
                mime="application/json",
                use_container_width=True,
            )

    with col2:
        if st.button(
            "📋 导出作答模板 (Markdown)", use_container_width=True, type="secondary"
        ):
            # 生成学生作答模板
            md_content = generate_answer_template(st.session_state.questions_data)
            filename = f"学生作答模板_{st.session_state.exam_title}.md"

            st.download_button(
                label="⬇️ 下载 Markdown 模板",
                data=md_content,
                file_name=filename,
                mime="text/markdown",
                use_container_width=True,
            )

    # 预览
    with st.expander("👀 预览作答模板"):
        md_content = generate_answer_template(st.session_state.questions_data)
        st.code(md_content, language="markdown")


def generate_answer_template(questions_data: list) -> str:
    """生成学生作答Markdown模板"""
    lines = ["# 学生作答模板", "", "**学生ID:** student_XXXX", "", "---", ""]

    for q in questions_data:
        is_composite = q.get("is_composite", False)

        if is_composite:
            # 大题
            lines.append(f"## {q['id']}. {q['description']}")
            lines.append("")

            for sq in q.get("sub_questions", []):
                lines.append(
                    f"### {sq['id']}. {sq['description']} ({sq['max_score']}分)"
                )
                lines.append("")
                lines.append(f"[作答: {sq['id']}]")
                lines.append("在此输入答案...")
                lines.append("")
        else:
            # 单题
            lines.append(f"## {q['id']}. {q['description']} ({q['max_score']}分)")
            lines.append("")
            lines.append(f"[作答: {q['id']}]")
            lines.append("在此输入答案...")
            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
