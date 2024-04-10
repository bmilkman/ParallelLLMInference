from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from starlette.responses import JSONResponse
import httpx
import asyncio
import uuid

app = FastAPI()
SUMMARIZE_APIS = 6
FEEDBACK_PORT = SUMMARIZE_APIS


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
# Creating an asyncio queue
task_queue = asyncio.Queue()

async def worker(api_url):
    async with httpx.AsyncClient() as client:
        while True:
            # Wait for an item from the queue
            task_id, item = await task_queue.get()
            try:
                response = await client.post(api_url, json=item.dict())
                results[task_id] = {'status' : 'completed', 'data':response.json()}
            except Exception as e:
                results[task_id] = {'status': 'error', 'data' :str(e)}
            finally:  
                #print("Processed:", response)
                task_queue.task_done()

@app.on_event("startup")
async def startup_event():
    api_urls = [f"http://0.0.0.0:500{i}/summarize" for i in range(SUMMARIZE_APIS)]
    # Create multiple worker tasks to process the queue concurrently
    for api_url in api_urls:
        asyncio.create_task(worker(api_url))
        print(f"Workers started for {api_url}")

@app.post("/summarize")
async def submit_data(item: SummarizeRequest):
    task_id = str(uuid.uuid4())
    await task_queue.put((task_id,item))
    return JSONResponse(content={"message": "Data added to queue", 'task_id' : task_id})

@app.get("/results/{task_id}")
async def get_result(task_id: str):
    result = results.get(task_id)
    if result and result["status"] == "completed":
        return result["data"]
    elif result and result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["data"])
    else:
        raise HTTPException(status_code=404, detail="Result not available or task not found")
        
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