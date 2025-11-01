"""
试卷制作表单逻辑
"""

import streamlit as st
import time
import json
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


def import_exam_config(uploaded_file):
    """从JSON文件导入试卷配置"""
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
    except Exception as e:
        st.error(f"❌ 导入失败: {str(e)}")


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
                    placeholder="小题参考答案...",
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
                        use_container_width=True,
                        key="add_subq_criterion_btn",
                    ):
                        st.session_state.adding_subq_criterion = True
                with col2:
                    crit_count = len(curr_subq["scoring_criteria"])
                    crit_total = sum(c["points"] for c in curr_subq["scoring_criteria"])
                    st.info(f"已添加 {crit_count} 项，共 {crit_total} 分")

                # 添加评分标准的表单
                if st.session_state.get("adding_subq_criterion", False):
                    with st.form(key="add_subq_criterion_form"):
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            subq_crit_points = st.number_input(
                                "分数 *", min_value=0.0, value=1.0, step=0.5
                            )
                        with col2:
                            subq_crit_desc = st.text_input(
                                "标准描述 *", placeholder="例如：正确说明..."
                            )

                        col1, col2 = st.columns(2)
                        with col1:
                            subq_submit = st.form_submit_button(
                                "✅ 确认", type="primary", use_container_width=True
                            )
                        with col2:
                            subq_cancel = st.form_submit_button(
                                "❌ 取消", use_container_width=True
                            )

                        if subq_cancel:
                            st.session_state.adding_subq_criterion = False
                            st.rerun()

                        if subq_submit:
                            if not subq_crit_desc:
                                st.error("请填写标准描述")
                            else:
                                curr_subq["scoring_criteria"].append(
                                    {
                                        "points": subq_crit_points,
                                        "criterion": subq_crit_desc,
                                    }
                                )
                                st.session_state.adding_subq_criterion = False
                                st.success("✅ 已添加")
                                time.sleep(0.3)
                                st.rerun()

                # 显示已添加的评分标准
                if curr_subq["scoring_criteria"]:
                    st.markdown("**📝 已添加的评分标准：**")
                    for idx, crit in enumerate(curr_subq["scoring_criteria"]):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.write(
                                f"{idx+1}. **{crit['points']}分** - {crit['criterion']}"
                            )
                        with col2:
                            if st.button("🗑️", key=f"del_subq_crit_{idx}", help="删除"):
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
                        temp["sub_questions"].append(curr_subq.copy())
                        del st.session_state.current_subquestion
                        st.session_state.adding_subquestion = False
                        if "adding_subq_criterion" in st.session_state:
                            del st.session_state.adding_subq_criterion
                        st.success(f"✅ 已添加小题: {curr_subq['id']}")
                        time.sleep(0.5)
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
                    st.write(f"**描述**: {sq['description']}")
                    st.write(f"**参考答案**: {sq['reference_answer']}")
                    st.write("**评分标准**:")
                    for crit in sq["scoring_criteria"]:
                        st.write(f"  - {crit['points']}分: {crit['criterion']}")

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
                    st.error("请填写所有必填字段（标记*）")
                elif not temp["sub_questions"]:
                    st.error("请至少添加一道小题")
                else:
                    # 计算大题总分
                    total_score = sum(sq["max_score"] for sq in temp["sub_questions"])

                    st.session_state.questions_data.append(
                        {
                            "id": temp["id"],
                            "type": temp["type"],
                            "description": temp["description"],
                            "max_score": total_score,
                            "is_composite": True,
                            "sub_questions": temp["sub_questions"],
                        }
                    )
                    # 清理临时数据
                    del st.session_state.composite_temp
                    del st.session_state.adding_question_type
                    if "adding_subquestion" in st.session_state:
                        del st.session_state.adding_subquestion
                    if "current_subquestion" in st.session_state:
                        del st.session_state.current_subquestion
                    if "adding_subq_criterion" in st.session_state:
                        del st.session_state.adding_subq_criterion

                    st.success(f"✅ 已添加大题: {temp['id']}（共{total_score}分）")
                    time.sleep(0.5)
                    st.rerun()

        with col2:
            if st.button("❌ 取消", use_container_width=True):
                # 清理临时数据
                del st.session_state.composite_temp
                del st.session_state.adding_question_type
                if "adding_subquestion" in st.session_state:
                    del st.session_state.adding_subquestion
                if "current_subquestion" in st.session_state:
                    del st.session_state.current_subquestion
                if "adding_subq_criterion" in st.session_state:
                    del st.session_state.adding_subq_criterion
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
                    # 大题展示
                    sub_count = len(q.get("sub_questions", []))
                    with st.expander(
                        f"📚 {idx+1}. {q['id']} - {q['description']} ({q['max_score']}分，含{sub_count}小题)",
                        expanded=False,
                    ):
                        st.write(f"**题目类型**: {q['type']}")
                        st.write(f"**总分**: {q['max_score']}分")
                        st.write("")
                        st.write("**小题列表**:")
                        for sidx, sq in enumerate(q.get("sub_questions", []), 1):
                            st.write(
                                f"  {sidx}. **{sq['id']}** ({sq['max_score']}分): {sq['description']}"
                            )
                            st.write(f"     参考答案: {sq['reference_answer']}")
                            st.write("     评分标准:")
                            for crit in sq.get("scoring_criteria", []):
                                st.write(
                                    f"       - {crit['points']}分: {crit['criterion']}"
                                )
                else:
                    # 单题展示
                    with st.expander(
                        f"📄 {idx+1}. {q['id']} - {q['description']} ({q['max_score']}分)",
                        expanded=False,
                    ):
                        st.write(f"**题目类型**: {q['type']}")
                        st.write(f"**满分**: {q['max_score']}分")
                        st.write(f"**参考答案**: {q['reference_answer']}")
                        st.write("**评分标准**:")
                        for crit in q.get("scoring_criteria", []):
                            st.write(f"  - {crit['points']}分: {crit['criterion']}")

            with col_btns:
                # 排序和删除按钮
                if idx > 0:
                    if st.button("⬆️", key=f"up_q_{idx}", help="上移"):
                        questions = st.session_state.questions_data
                        questions[idx], questions[idx - 1] = (
                            questions[idx - 1],
                            questions[idx],
                        )
                        st.rerun()

                if idx < len(st.session_state.questions_data) - 1:
                    if st.button("⬇️", key=f"down_q_{idx}", help="下移"):
                        questions = st.session_state.questions_data
                        questions[idx], questions[idx + 1] = (
                            questions[idx + 1],
                            questions[idx],
                        )
                        st.rerun()

                if st.button("🗑️", key=f"del_q_{idx}", help="删除"):
                    st.session_state.questions_data.pop(idx)
                    st.rerun()


def show_export_section():
    """导出功能区域"""
    from src.ui.utils.formatters import generate_answer_template

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
