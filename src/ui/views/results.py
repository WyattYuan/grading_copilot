"""
评分结果页面
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from src.ui.utils.formatters import format_job_display_name
from src.ui.utils.api_client import get_job_summary
from src.ui.components.student_detail import show_student_detail


def show_results_page():
    """查看评分结果页面 - 增强版with数据可视化"""
    st.header("📈 评分结果")

    # 选择历史任务
    job_id = st.session_state.get("current_job_id", "")

    if st.session_state.app_jobs:
        # 如果有current_job_id且在列表中，设置为默认值
        default_index = 0
        if job_id:
            job_ids = [job["job_id"] for job in st.session_state.app_jobs]
            if job_id in job_ids:
                default_index = job_ids.index(job_id) + 1  # +1因为第一个是空选项

        # 创建任务选项映射（友好显示）
        job_options_map = {"": "请选择任务..."}
        for job in st.session_state.app_jobs:
            display_name = format_job_display_name(job)
            job_options_map[job["job_id"]] = display_name

        job_options = [""] + [job["job_id"] for job in st.session_state.app_jobs]
        selected_job = st.selectbox(
            "选择任务",
            job_options,
            index=default_index,
            format_func=lambda x: job_options_map.get(x, "请选择任务..."),
            key="results_history_select",
        )
        if selected_job:
            job_id = selected_job
            st.session_state.current_job_id = job_id
    else:
        st.info("💡 暂无历史任务，请先创建评分任务")
        return

    if job_id:
        # 获取总分表
        with st.spinner("📊 正在加载数据..."):
            summary_data = get_job_summary(job_id)
        
        if not summary_data:
            return
        
        df = pd.DataFrame(summary_data["data"])

        if df.empty:
            st.warning("⚠️ 该任务暂无评分数据")
            return

        # ========== 数据可视化部分 ==========
        st.subheader("📊 数据可视化")

        # 创建可视化标签页
        viz_tab1, viz_tab2, viz_tab3 = st.tabs(
            ["📈 总体统计", "📊 分数分布", "🎯 题目分析"]
        )

        with viz_tab1:
            # 总体统计
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

            # 添加更多统计指标
            col1, col2, col3, col4 = st.columns(4)

            with col1:
                median_score = df["total_score"].median()
                st.metric("中位数", f"{median_score:.2f}")

            with col2:
                std_score = df["total_score"].std()
                st.metric("标准差", f"{std_score:.2f}")

            with col3:
                pass_rate = (df["total_score"] >= 60).mean() * 100
                st.metric("及格率", f"{pass_rate:.1f}%")

            with col4:
                excellent_rate = (df["total_score"] >= 85).mean() * 100
                st.metric("优秀率", f"{excellent_rate:.1f}%")

        with viz_tab2:
            # 分数分布图
            col1, col2 = st.columns([2, 1])

            with col1:
                # 直方图
                fig_hist = px.histogram(
                    df,
                    x="total_score",
                    nbins=20,
                    title="分数分布直方图",
                    labels={"total_score": "总分", "count": "学生数"},
                    color_discrete_sequence=["#1f77b4"],
                )
                fig_hist.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig_hist, use_container_width=True)

            with col2:
                # 箱线图
                fig_box = px.box(
                    df,
                    y="total_score",
                    title="分数箱线图",
                    labels={"total_score": "总分"},
                    color_discrete_sequence=["#2ca02c"],
                )
                fig_box.update_layout(height=400)
                st.plotly_chart(fig_box, use_container_width=True)

            # 分数段分布
            st.markdown("#### 📊 分数段分布")
            score_ranges = pd.cut(
                df["total_score"],
                bins=[0, 60, 70, 80, 90, 100],
                labels=[
                    "不及格(<60)",
                    "及格(60-70)",
                    "中等(70-80)",
                    "良好(80-90)",
                    "优秀(90-100)",
                ],
            )
            range_counts = score_ranges.value_counts().sort_index()

            fig_pie = px.pie(
                values=range_counts.values,
                names=range_counts.index,
                title="分数段占比",
                color_discrete_sequence=px.colors.sequential.RdBu,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with viz_tab3:
            # 题目分析（如果有题目列信息）
            question_cols = [
                col
                for col in df.columns
                if col.startswith("q") and col != "total_score"
            ]

            if question_cols:
                st.markdown("#### 📝 各题平均分")

                # 计算每题平均分
                question_stats = []
                for q_col in question_cols:
                    if q_col in df.columns:
                        avg = df[q_col].mean()
                        question_stats.append({"题目": q_col, "平均分": avg})

                if question_stats:
                    q_df = pd.DataFrame(question_stats)

                    # 柱状图
                    fig_bar = px.bar(
                        q_df,
                        x="题目",
                        y="平均分",
                        title="各题平均分对比",
                        labels={"平均分": "平均分", "题目": "题目编号"},
                        color="平均分",
                        color_continuous_scale="Viridis",
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)

                    # 数据表格
                    st.dataframe(q_df, use_container_width=True, hide_index=True)
            else:
                st.info("💡 当前数据不包含单题分数信息")

        st.markdown("---")

        # 显示总分表
        st.subheader("📋 总分表")
        st.caption("💡 提示：点击列标题可以排序")

        # 直接显示数据框，利用 Streamlit 自带的排序功能
        st.dataframe(df, use_container_width=True, hide_index=True)

        # 下载按钮
        col1, col2 = st.columns([1, 1])
        with col1:
            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 下载CSV",
                data=csv,
                file_name=f"{job_id}_summary.csv",
                mime="text/csv",
                key="results_download_csv",
                use_container_width=True,
            )
        with col2:
            # Excel下载（如果需要可以添加）
            pass

        # 选择学生查看详情
        st.markdown("---")
        st.subheader("🔍 查看学生详情")

        col1, col2 = st.columns([3, 1])
        with col1:
            selected_student = st.selectbox(
                "选择学生",
                df["student_id"].tolist(),
                index=None,
                key="results_student_select",
                format_func=lambda x: (
                    f"{x} - {df[df['student_id']==x]['total_score'].values[0]:.1f}分"
                    if x
                    else "请选择..."
                ),
            )
        with col2:
            if selected_student:
                if st.button("📊 查看详情", use_container_width=True):
                    pass  # 详情会在下方自动显示

        if selected_student:
            show_student_detail(job_id, selected_student)
