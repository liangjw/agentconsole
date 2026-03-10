from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.database import engine, Base
from backend.app.api import agents, conversations, skills, templates

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgentConsole API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents.router, prefix="/api/agents", tags=["agents"])
app.include_router(conversations.router, prefix="/api/conversations", tags=["conversations"])
app.include_router(skills.router, prefix="/api/skills", tags=["skills"])
app.include_router(templates.router, prefix="/api/templates", tags=["templates"])

@app.get("/")
def read_root():
    return {"message": "AgentConsole API"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
