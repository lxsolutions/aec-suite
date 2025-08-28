


from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for all domains (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AEC Orchestrator Backend"}

# Health check endpoint
@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "0.1.0"}


