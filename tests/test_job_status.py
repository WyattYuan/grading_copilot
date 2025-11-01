"""测试任务状态持久化"""

from src.api.file_utils import job_exists, load_job_status, save_job_status

# 测试任务ID
job_id = "job_a1afa040f91f"

print(f"✅ 测试任务: {job_id}")
print(f"📁 任务存在: {job_exists(job_id)}")

status = load_job_status(job_id)
if status:
    print(f"📊 状态数据: {status}")
else:
    print("⚠️  没有找到状态文件，创建测试状态...")
    test_status = {
        "job_id": job_id,
        "status": "completed",
        "total_questions": 3,
        "processed_questions": 3,
        "created_at": "2025-10-31T10:00:00",
        "updated_at": "2025-10-31T10:05:00",
    }
    save_job_status(job_id, test_status)
    print(f"✅ 已创建状态文件")
    status = load_job_status(job_id)
    print(f"📊 状态数据: {status}")
