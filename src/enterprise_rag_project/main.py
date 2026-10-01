from fastapi import FastAPI
from contextlib import asynccontextmanager

from enterprise_rag_project.ingestion.vectore_store import initialize_collection
from enterprise_rag_project.api.chat import router as chat_router
from enterprise_rag_project.api.upload_documents import router as documents_router
from enterprise_rag_project.api.register import router as register_router
from enterprise_rag_project.api.login import router as login_router
from enterprise_rag_project.db.checkpointer import get_checkpointer
from enterprise_rag_project.agents.graph import build_graph
from enterprise_rag_project.api.conversations import router as conversations_router
from enterprise_rag_project.api.get_documents import router as get_documents_router
from enterprise_rag_project.db.connection import engine
from enterprise_rag_project.db.base import Base
from dotenv import load_dotenv

load_dotenv()




@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    initialize_collection()
    with get_checkpointer() as checkpointer:

        app.state.graph = build_graph(
            checkpointer
        )

        yield

app = FastAPI(title="Enterprise Knowledge & Support Agent",lifespan=lifespan)

app.include_router(chat_router)
app.include_router(documents_router)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(conversations_router)
app.include_router(get_documents_router)
