# 性能优化文档

## 并发评分优化

### 问题分析

**原有问题：**
- 串行处理：每次只评一道题，评完一道才评下一道
- 效率低下：假设每道题评分耗时 3 秒
  - 3 个学生 × 3 道题 = 9 道题
  - 串行总耗时：9 × 3 = 27 秒
  
### 优化方案

**并发处理：**
- 使用 `asyncio.gather()` 并发执行多个评分任务
- 分批处理避免资源过载
- 并发总耗时：取决于批次数和批量大小

**性能提升：**
```
假设：10 个学生 × 5 道题 = 50 道题，每题 3 秒

串行处理：
  总耗时 = 50 × 3 = 150 秒 (2.5 分钟)

并发处理（批量=10）：
  批次数 = 50 ÷ 10 = 5 批
  总耗时 = 5 × 3 = 15 秒
  
性能提升：10 倍！
```

### 实现细节

#### 1. 核心改进

**之前（串行）：**
```python
for answer_file in answer_files:
    student_answer = FileParser.parse_student_answer(answer_file)
    for question in exam_config.questions:
        # 等待上一个评完才评下一个 ❌
        result = await grading_agent.grade(question, student_ans_text)
        save_report(result)
```

**现在（并发）：**
```python
# 1. 收集所有任务
tasks = []
for answer_file in answer_files:
    for question in exam_config.questions:
        task = grade_single_answer(student_answer, question)
        tasks.append(task)

# 2. 分批并发执行
batch_size = 10
for i in range(0, len(tasks), batch_size):
    batch_tasks = tasks[i:i + batch_size]
    # 同时执行 10 个评分任务 ✅
    results = await asyncio.gather(*batch_tasks)
    save_results(results)
```

#### 2. 批量处理策略

**为什么要分批？**
- 避免同时创建太多并发任务
- 控制内存使用
- 避免 API 限流
- 更好的进度跟踪

**批量大小选择：**
- 默认：10（可配置）
- 太小：无法充分利用并发
- 太大：可能导致资源耗尽或 API 限流

#### 3. 错误处理

```python
# 使用 return_exceptions=True 确保一个任务失败不影响其他任务
results = await asyncio.gather(*batch_tasks, return_exceptions=True)

for result in results:
    if isinstance(result, GradingReport):
        # 成功的报告
        save_report(result)
    elif isinstance(result, Exception):
        # 失败的任务，记录日志
        print(f"评分任务异常: {str(result)}")
```

### 配置参数

可以通过环境变量调整并发参数：

```bash
# .env 文件
GRADING_BATCH_SIZE=10        # 每批并发处理的任务数
MAX_CONCURRENT_TASKS=50      # 最大并发任务数（预留）
```

**调优建议：**
- CPU密集型任务：`batch_size = CPU核心数 × 2`
- IO密集型任务（AI API）：`batch_size = 10-50`
- 根据 API 限流调整

### 性能对比

| 场景                  | 串行耗时        | 并发耗时 (batch=10) | 提升倍数 |
| --------------------- | --------------- | ------------------- | -------- |
| 10学生×3题 (30题)     | 90秒            | 9秒                 | 10x      |
| 30学生×5题 (150题)    | 450秒 (7.5分钟) | 45秒                | 10x      |
| 100学生×10题 (1000题) | 3000秒 (50分钟) | 300秒 (5分钟)       | 10x      |

*假设每题评分耗时 3 秒，实际耗时取决于 AI 模型响应速度*

### 进一步优化建议

#### 1. 使用信号量限制并发数

```python
# 限制同时并发的最大任务数
semaphore = asyncio.Semaphore(config.MAX_CONCURRENT_TASKS)

async def grade_with_semaphore(student_answer, question):
    async with semaphore:
        return await grade_single_answer(student_answer, question)
```

#### 2. 使用连接池

```python
# LangChain 已经内部管理了 HTTP 连接池
# 确保不要为每个任务创建新的 GradingAgent
grading_agent = GradingAgent()  # 复用同一个实例
```

#### 3. 缓存评分结果

```python
# 如果相同的答案被重复评分，可以缓存
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_cached_grade(question_id, answer_hash):
    # 返回缓存的评分结果
    pass
```

#### 4. 使用任务队列（大规模场景）

对于超大规模评分（数千学生），可以考虑：
- Celery + Redis
- RabbitMQ
- AWS SQS

### 监控指标

建议监控以下指标：
- 平均评分耗时
- 并发任务数
- 成功率 / 失败率
- API 调用频率
- 内存使用

### 注意事项

1. **API 限流**
   - 确保并发数不超过 API 提供商的限制
   - OpenAI 有 RPM (Requests Per Minute) 限制
   
2. **内存管理**
   - 不要一次性加载所有任务到内存
   - 使用生成器或分批处理

3. **错误重试**
   - 对失败的任务实现重试机制
   - 使用指数退避策略

4. **进度跟踪**
   - 确保并发情况下进度更新准确
   - 使用原子操作更新计数器

### 代码位置

- **核心实现**: `src/api/main.py` - `process_grading_job()`
- **配置文件**: `src/config.py` - `Config`
- **评分代理**: `src/agents/grading_agent.py` - `GradingAgent`

### 测试验证

```python
# 测试并发性能
import time

start = time.time()
# 运行评分任务
end = time.time()

print(f"评分总耗时: {end - start:.2f} 秒")
print(f"平均每题: {(end - start) / total_questions:.2f} 秒")
```

## 总结

通过引入并发评分机制：
- ✅ **性能提升 10 倍**（batch_size=10 时）
- ✅ **充分利用 async/await**
- ✅ **可配置的批量大小**
- ✅ **完善的错误处理**
- ✅ **实时进度跟踪**

这是一个简单而有效的优化，无需引入复杂的分布式系统，就能显著提升评分效率！
