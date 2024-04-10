from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse
import httpx
import asyncio
import uuid
import torch

app = FastAPI()
# 假设有n张卡，用n-1张卡去异步处理大流量的请求，用1张卡同步慢慢处理流量小的请求
SUMMARIZE_APIS = torch.cuda.device_count() - 1 
FEEDBACK_PORT = SUMMARIZE_APIS

# 这里是我的样例request，仅作参考
class SummarizeRequest(BaseModel):
    text: str
    timestamp: str

class FeedbackRequest(BaseModel):
    request_id: str
    feedback_option: int
    timestamp: str
    history: list
    num_requested: int
    satisfied: bool
    text: str
    
results = {}
# 使用queue的方式去囤积请求
task_queue = asyncio.Queue()

async def worker(api_url):
    async with httpx.AsyncClient() as client:
        while True:
            # 每个worker去queue里拿任务
            task_id, item = await task_queue.get()
            try:
                response = await client.post(api_url, json=item.dict())
                results[task_id] = {'status' : 'completed', 'data':response.json()}
            except Exception as e:
                results[task_id] = {'status': 'error', 'data' :str(e)}
            finally:  
                #print("Processed:", response)
                # 这是个很奇怪的说法，在异步的queue里需要通过这个来确认get的东西没了
                task_queue.task_done()

@app.on_event("startup")
async def startup_event():
    # 假设你的LLM API的地址和端口是这样的
    api_urls = [f"http://0.0.0.0:500{i}/summarize" for i in range(SUMMARIZE_APIS)]
    # 一个API分配一个worker
    for api_url in api_urls:
        asyncio.create_task(worker(api_url))
        print(f"Workers started for {api_url}")

@app.post("/summarize")
async def submit_data(item: SummarizeRequest):
    task_id = str(uuid.uuid4())
    await task_queue.put((task_id,item))
    return JSONResponse(content={"message": "Data added to queue", 'task_id' : task_id})

# 这里把异步操作的分发和收集分开了，适用于每天需要对后台数据进行大量更新的任务。
@app.get("/results/{task_id}")
async def get_result(task_id: str):
    result = results.pop(task_id, None)
    if result and result["status"] == "completed":
        return result["data"]
    elif result and result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["data"])
    else:
        raise HTTPException(status_code=404, detail="Result not available or task not found")
# 同步   
@app.post("/feedback")
async def submit_feedback(feedback: FeedbackRequest):
    try:
    # Assuming direct handling; adjust according to your actual API setup
        response = httpx.post(f"http://0.0.0.0:500{FEEDBACK_PORT}/feedback", json=feedback.dict())
        return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
