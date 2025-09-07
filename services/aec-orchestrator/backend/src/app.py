




from fastapi import FastAPI
from .main import app as main_app

# Import models to register them with SQLAlchemy
from .models import User, Project, AgentRun, KnowledgeBase

app = FastAPI()

# Include the main router
@app.get("/")
def read_root():
    return {"message": "AEC Orchestrator Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

