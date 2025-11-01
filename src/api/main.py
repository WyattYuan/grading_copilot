"""
FastAPI 主应用
"""

from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from typing import Dict, Optional
import json
import uuid
from datetime import datetime

from src.models import JobStatus, UpdateReportRequest, GradingReport, QuestionSnapshot
from src.config import config
from src.api.file_utils import (
    FileParser,
    ReportManager,
    save_job_status,
    load_job_status,
    job_exists,
)
from src.api.sync_manager import SyncManager
from src.agents import GradingAgent

# 确保必要的目录存在
config.ensure_dirs()

# 创建FastAPI应用
app = FastAPI(
    title="AI智能评分系统API",
    description="人机协同的智能评分与分析系统",
    version="0.1.0",
)

# 添加CORS中间件,允许Streamlit访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局任务状态存储 (生产环境应使用数据库)
job_statuses: Dict[str, JobStatus] = {}


def get_or_load_job_status(job_id: str) -> Optional[JobStatus]:
    """
    获取任务状态，如果内存中没有则从文件加载

    Args:
        job_id: 任务ID

    Returns:
        JobStatus: 任务状态对象，如果不存在返回None
    """
    # 先检查内存
    if job_id in job_statuses:
        return job_statuses[job_id]

    # 尝试从文件加载
    status_data = load_job_status(job_id)
    if status_data:
        # 将字典转换为JobStatus对象
        job_status = JobStatus(**status_data)
        # 缓存到内存
        job_statuses[job_id] = job_status
        return job_status

    return None


@app.get("/")
async def root():
    """健康检查"""
    return {"status": "running", "message": "AI智能评分系统API"}


@app.get("/api/v1/jobs")
async def list_all_jobs():
    """
    获取所有任务列表

    Returns:
        Dict: 包含任务列表的响应
    """
    from src.api.file_utils import get_all_jobs

    jobs = get_all_jobs()
    return {"jobs": jobs, "total": len(jobs)}


@app.post("/api/v1/jobs/start")
async def start_grading_job(
    background_tasks: BackgroundTasks,
    exam_config: UploadFile = File(..., description="考试配置JSON文件"),
    student_answers: UploadFile = File(..., description="学生答案ZIP压缩包"),
):
    """
    启动评分任务

    Args:
        exam_config: 考试配置JSON文件
        student_answers: 学生答案ZIP压缩包

    Returns:
        Dict: 包含job_id的响应
    """
    # 生成唯一的任务ID
    job_id = f"job_{uuid.uuid4().hex[:12]}"

    # 创建任务上传目录
    upload_dir = config.UPLOADS_DIR / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)

    # 保存上传的文件
    config_path = upload_dir / "exam_config.json"
    zip_path = upload_dir / "student_answers.zip"

    # 保存考试配置
    with open(config_path, "wb") as f:
        f.write(await exam_config.read())

    # 保存ZIP文件
    with open(zip_path, "wb") as f:
        f.write(await student_answers.read())

    # 初始化任务状态
    job_status = JobStatus(
        job_id=job_id,
        status="pending",
        total_questions=0,
        processed_questions=0,
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    job_statuses[job_id] = job_status

    # 保存状态到文件
    save_job_status(job_id, job_status.model_dump(mode="json"))

    # 在后台启动评分任务
    background_tasks.add_task(process_grading_job, job_id, config_path, zip_path)

    return {"job_id": job_id, "status": "pending", "message": "评分任务已启动"}


async def process_grading_job(job_id: str, config_path: Path, zip_path: Path):
    """
    后台处理评分任务

    Args:
        job_id: 任务ID
        config_path: 考试配置文件路径
        zip_path: 学生答案ZIP文件路径
    """
    import asyncio

    try:
        # 更新状态为运行中
        job_statuses[job_id].status = "running"
        job_statuses[job_id].updated_at = datetime.now()
        save_job_status(job_id, job_statuses[job_id].model_dump(mode="json"))

        # 1. 解析考试配置
        exam_config = FileParser.parse_exam_config(config_path)

        # 2. 解压学生答案
        extract_dir = config_path.parent / "answers"
        answer_files = FileParser.extract_zip(zip_path, extract_dir)

        # 3. 计算总题目数
        total_questions = len(answer_files) * len(exam_config.questions)
        job_statuses[job_id].total_questions = total_questions
        save_job_status(job_id, job_statuses[job_id].model_dump(mode="json"))

        # 4. 初始化评分代理
        grading_agent = GradingAgent()

        # 5. 创建所有评分任务（并发执行）
        async def grade_single_answer(student_answer, question):
            """评分单个题目"""
            try:
                student_ans_text = student_answer.answers.get(question.id, "")

                if not student_ans_text:
                    return None

                # 调用AI评分
                grading_result = await grading_agent.grade(question, student_ans_text)

                # 创建评分报告
                report = GradingReport(
                    student_info=student_answer.student_info,
                    question_id=question.id,
                    task_id=job_id,
                    question_snapshot=QuestionSnapshot(
                        description=question.description,
                        max_score=question.get_max_score(),
                        reference_answer=question.get_reference_answer(),
                    ),
                    student_answer=student_ans_text,
                    ai_score=grading_result.score,
                    ai_rationale=grading_result.rationale,
                    final_score=grading_result.score,
                    human_override_rationale=None,
                    last_modified_by="AI",
                )

                return report
            except Exception as e:
                print(
                    f"评分失败 - 学生: {student_answer.student_info.student_id}, 题目: {question.id}, 错误: {str(e)}"
                )
                return None

        # 收集所有任务
        tasks = []
        task_info = []  # 用于跟踪任务信息

        for answer_file in answer_files:
            try:
                student_answer = FileParser.parse_student_answer(answer_file)
                for question in exam_config.questions:
                    task = grade_single_answer(student_answer, question)
                    tasks.append(task)
                    task_info.append(
                        {
                            "student_id": student_answer.student_info.student_id,
                            "question_id": question.id,
                        }
                    )
            except Exception as e:
                print(f"解析学生答案失败 {answer_file.name}: {str(e)}")
                continue

        # 并发执行所有评分任务（分批处理避免过载）
        batch_size = config.GRADING_BATCH_SIZE
        all_reports = []

        for i in range(0, len(tasks), batch_size):
            batch_tasks = tasks[i : i + batch_size]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)

            # 保存报告并更新进度
            for result in batch_results:
                if isinstance(result, GradingReport):
                    ReportManager.save_report(result, job_id)
                    all_reports.append(result)
                elif isinstance(result, Exception):
                    print(f"评分任务异常: {str(result)}")

            # 更新进度
            processed = i + len(batch_tasks)
            job_statuses[job_id].processed_questions = min(processed, total_questions)
            job_statuses[job_id].updated_at = datetime.now()
            save_job_status(job_id, job_statuses[job_id].model_dump(mode="json"))

        # 6. 生成总分表
        SyncManager.regenerate_summary_table(job_id)

        # 7. 更新状态为完成
        job_statuses[job_id].status = "completed"
        job_statuses[job_id].updated_at = datetime.now()
        save_job_status(job_id, job_statuses[job_id].model_dump(mode="json"))

    except Exception as e:
        # 发生错误
        job_statuses[job_id].status = "failed"
        job_statuses[job_id].error_message = str(e)
        job_statuses[job_id].updated_at = datetime.now()
        save_job_status(job_id, job_statuses[job_id].model_dump(mode="json"))
        print(f"任务 {job_id} 失败: {str(e)}")


@app.get("/api/v1/jobs/{job_id}/status")
async def get_job_status(job_id: str):
    """
    获取任务状态

    Args:
        job_id: 任务ID

    Returns:
        JobStatus: 任务状态信息
    """
    job_status = get_or_load_job_status(job_id)
    if not job_status:
        raise HTTPException(status_code=404, detail="任务不存在")

    return job_status


@app.get("/api/v1/jobs/{job_id}/summary")
async def get_summary_table(job_id: str):
    """
    获取总分表

    Args:
        job_id: 任务ID

    Returns:
        Dict: 总分表数据
    """
    # 检查任务是否存在
    if not job_exists(job_id):
        raise HTTPException(status_code=404, detail="任务不存在")

    # 检查任务状态（如果有的话）
    job_status = get_or_load_job_status(job_id)
    if job_status and job_status.status != "completed":
        raise HTTPException(status_code=400, detail="任务尚未完成")

    try:
        df = SyncManager.get_summary_table(job_id)
        return {"columns": df.columns.tolist(), "data": df.to_dict(orient="records")}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取总分表失败: {str(e)}")


@app.get("/api/v1/jobs/{job_id}/summary/download")
async def download_summary_table(job_id: str):
    """
    下载总分表CSV文件

    Args:
        job_id: 任务ID

    Returns:
        FileResponse: CSV文件
    """
    if not job_exists(job_id):
        raise HTTPException(status_code=404, detail="任务不存在")

    csv_path = config.REPORTS_DIR / job_id / "summary_table.csv"

    if not csv_path.exists():
        raise HTTPException(status_code=404, detail="总分表文件不存在")

    return FileResponse(
        csv_path, media_type="text/csv", filename=f"{job_id}_summary.csv"
    )


@app.get("/api/v1/jobs/{job_id}/students/{student_id}")
async def get_student_detail(job_id: str, student_id: str):
    """
    获取学生的详细评分信息

    Args:
        job_id: 任务ID
        student_id: 学生ID

    Returns:
        Dict: 学生详细信息
    """
    if not job_exists(job_id):
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        return SyncManager.get_student_detail(job_id, student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取学生信息失败: {str(e)}")


@app.get("/api/v1/jobs/{job_id}/reports/{student_id}/{question_id}")
async def get_report(job_id: str, student_id: str, question_id: str):
    """
    获取单个评分报告

    Args:
        job_id: 任务ID
        student_id: 学生ID
        question_id: 题目ID

    Returns:
        GradingReport: 评分报告
    """
    if not job_exists(job_id):
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        report = ReportManager.load_report(job_id, student_id, question_id)
        return report
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="报告不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取报告失败: {str(e)}")


@app.put("/api/v1/jobs/{job_id}/reports/{student_id}/{question_id}")
async def update_report(
    job_id: str, student_id: str, question_id: str, update_data: UpdateReportRequest
):
    """
    更新评分报告 (人工微调)

    这是确保数据一致性的关键接口:
    更新报告后会自动重新生成总分表

    Args:
        job_id: 任务ID
        student_id: 学生ID
        question_id: 题目ID
        update_data: 更新数据

    Returns:
        Dict: 更新后的报告
    """
    if not job_exists(job_id):
        raise HTTPException(status_code=404, detail="任务不存在")

    try:
        # 更新报告
        updated_report = ReportManager.update_report(
            job_id=job_id,
            student_id=student_id,
            question_id=question_id,
            new_score=update_data.new_score,
            new_rationale=update_data.new_rationale,
            modified_by=update_data.modified_by,
        )

        # 关键: 自动重新生成总分表
        SyncManager.on_report_updated(job_id)

        return {"message": "报告更新成功,总分表已同步", "report": updated_report}

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="报告不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新报告失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=config.API_HOST, port=config.API_PORT)
