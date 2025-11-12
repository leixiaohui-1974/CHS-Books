"""
简单的Web服务器测试
"""

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pathlib import Path

app = FastAPI()

BACKEND_DIR = Path(__file__).parent
FRONTEND_DIR = BACKEND_DIR.parent / "frontend"

@app.get("/", response_class=HTMLResponse)
async def root():
    """返回前端页面"""
    index_file = FRONTEND_DIR / "index.html"
    print(f"Looking for: {index_file}")
    print(f"Exists: {index_file.exists()}")
    
    if index_file.exists():
        content = index_file.read_text(encoding='utf-8')
        print(f"Content length: {len(content)}")
        return HTMLResponse(content=content)
    else:
        return HTMLResponse(content="<h1>File not found</h1>")

if __name__ == "__main__":
    import uvicorn
    print(f"Backend directory: {BACKEND_DIR}")
    print(f"Frontend directory: {FRONTEND_DIR}")
    print(f"Index file exists: {(FRONTEND_DIR / 'index.html').exists()}")
    uvicorn.run(app, host="0.0.0.0", port=8001)



