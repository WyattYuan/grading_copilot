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


def main():
    """主界面"""
    st.set_page_config(page_title="AI智能评分系统", page_icon="📝", layout="wide")

    st.title("🎓 AI智能评分系统")

    # 使用标签页导航 - 更直观的页签式界面
    tab1, tab2, tab3, tab4 = st.tabs(
        ["📤 新建评分任务", "📊 任务状态", "📋 评分结果", "✏️ 人工微调"]
    )

    with tab1:
        show_new_job_page()

    with tab2:
        show_job_status_page()

    with tab3:
        show_results_page()

    with tab4:
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
    - 文件名: `student_XXX.txt` 或 `student_XXX.docx`
    - 内容格式:
    ```
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

                # 保存到session state
                if "job_ids" not in st.session_state:
                    st.session_state.job_ids = []
                st.session_state.job_ids.append(job_id)

            except Exception as e:
                st.error(f"❌ 任务创建失败: {str(e)}")


def show_job_status_page():
    """查看任务状态页面"""
    st.header("📊 任务状态监控")

    # 输入任务ID
    job_id = st.text_input(
        "输入任务ID", placeholder="job_xxxxxxxxxxxx", key="status_job_id"
    )

    # 如果有历史任务,显示选择
    if "job_ids" in st.session_state and st.session_state.job_ids:
        st.markdown("**或选择历史任务:**")
        selected_job = st.selectbox(
            "历史任务",
            st.session_state.job_ids,
            index=None,
            key="status_history_select",
        )
        if selected_job:
            job_id = selected_job

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

    # 获取任务ID - 支持历史任务选择
    job_id = st.session_state.get("current_job_id", "")

    col1, col2 = st.columns([3, 1])

    with col1:
        job_id = st.text_input(
            "输入任务ID",
            value=job_id,
            placeholder="job_xxxxxxxxxxxx",
            key="results_job_id",
        )

    with col2:
        st.write("")  # 占位,对齐高度
        st.write("")
        # 历史任务选择
        if "job_ids" in st.session_state and st.session_state.job_ids:
            selected_job = st.selectbox(
                "或选择历史任务",
                [""] + st.session_state.job_ids,
                format_func=lambda x: "请选择..." if x == "" else x,
                key="results_history_select",
            )
            if selected_job:
                job_id = selected_job
                st.session_state.current_job_id = job_id

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

        st.markdown(f"### 学生: {student_id}")
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

    # 任务ID输入 - 支持历史任务选择
    col1, col2 = st.columns([3, 1])

    with col1:
        job_id = st.text_input(
            "任务ID", placeholder="job_xxxxxxxxxxxx", key="adjustment_job_id"
        )

    with col2:
        st.write("")  # 占位,对齐高度
        st.write("")
        # 历史任务选择
        if "job_ids" in st.session_state and st.session_state.job_ids:
            selected_job = st.selectbox(
                "或选择历史任务",
                [""] + st.session_state.job_ids,
                format_func=lambda x: "请选择..." if x == "" else x,
                key="adjustment_history_select",
            )
            if selected_job:
                job_id = selected_job

    if not job_id:
        st.info("👆 请先输入任务ID或选择历史任务")
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

        st.subheader(f"� 学生 {student_id} 的评分报告")

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


if __name__ == "__main__":
    main()
