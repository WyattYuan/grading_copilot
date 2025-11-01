"""
API 客户端封装
统一管理所有后端 API 调用
"""

import requests
import streamlit as st
from typing import Dict, Any, List, Optional
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).parent.parent.parent.parent))
from src.config import config

API_BASE_URL = f"http://{config.API_HOST}:{config.API_PORT}/api/v1"


def check_api_connection() -> tuple[bool, str]:
    """检查API连接状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs", timeout=3)
        response.raise_for_status()
        return True, "✅ 后端服务正常"
    except requests.exceptions.Timeout:
        return False, "⏱️ 连接超时，请检查后端服务是否启动"
    except requests.exceptions.ConnectionError:
        return (
            False,
            f"❌ 无法连接到后端服务 ({config.API_HOST}:{config.API_PORT})，请先启动 API 服务",
        )
    except requests.exceptions.HTTPError as e:
        return False, f"❌ HTTP错误: {e.response.status_code}"
    except Exception as e:
        return False, f"❌ 未知错误: {str(e)}"


@st.cache_data(ttl=30)
def load_job_history() -> List[Dict[str, Any]]:
    """从API加载任务历史（带缓存）"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs", timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["jobs"]
    except requests.exceptions.Timeout:
        st.error("⏱️ 请求超时，请稍后重试")
        return []
    except requests.exceptions.ConnectionError:
        st.error(f"❌ 无法连接到后端服务，请检查 API 是否启动")
        return []
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ HTTP错误 {e.response.status_code}: {e.response.text}")
        return []
    except Exception as e:
        st.error(f"❌ 加载任务历史失败: {str(e)}")
        return []


def handle_api_error(error: Exception, context: str = "操作") -> None:
    """统一的API错误处理"""
    if isinstance(error, requests.exceptions.Timeout):
        st.error(f"⏱️ {context}超时，请稍后重试")
    elif isinstance(error, requests.exceptions.ConnectionError):
        st.error(f"❌ 无法连接到后端服务，请检查 API 是否启动")
    elif isinstance(error, requests.exceptions.HTTPError):
        status_code = error.response.status_code
        if status_code == 404:
            st.error(f"❌ 资源不存在")
        elif status_code == 400:
            st.error(f"⚠️ 请求参数错误: {error.response.text}")
        elif status_code == 500:
            st.error(f"❌ 服务器内部错误")
        else:
            st.error(f"❌ HTTP错误 {status_code}: {error.response.text}")
    else:
        st.error(f"❌ {context}失败: {str(error)}")


def create_grading_job(
    exam_config_file, student_answers_file
) -> Optional[Dict[str, Any]]:
    """创建评分任务"""
    try:
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

        response = requests.post(f"{API_BASE_URL}/jobs/start", files=files, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        handle_api_error(e, "创建任务")
        return None


def get_job_status(job_id: str) -> Optional[Dict[str, Any]]:
    """获取任务状态"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}/status", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        handle_api_error(e, "获取任务状态")
        return None


def get_job_summary(job_id: str) -> Optional[Dict[str, Any]]:
    """获取任务总结"""
    try:
        response = requests.get(f"{API_BASE_URL}/jobs/{job_id}/summary", timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        handle_api_error(e, "获取结果")
        return None


def get_student_detail(job_id: str, student_id: str) -> Optional[Dict[str, Any]]:
    """获取学生详情"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/jobs/{job_id}/students/{student_id}", timeout=10
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        handle_api_error(e, "获取学生详情")
        return None


def update_question_score(
    job_id: str,
    student_id: str,
    question_id: str,
    new_score: float,
    rationale: str,
    modified_by: str,
) -> bool:
    """更新问题分数"""
    try:
        payload = {
            "new_score": new_score,
            "rationale": rationale,
            "modified_by": modified_by,
        }

        response = requests.put(
            f"{API_BASE_URL}/jobs/{job_id}/students/{student_id}/questions/{question_id}",
            json=payload,
            timeout=10,
        )
        response.raise_for_status()
        return True
    except Exception as e:
        handle_api_error(e, "更新分数")
        return False


def delete_job(job_id: str) -> bool:
    """删除任务"""
    try:
        response = requests.delete(f"{API_BASE_URL}/jobs/{job_id}", timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        handle_api_error(e, "删除任务")
        return False
