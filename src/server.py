from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import sys
import os
from datetime import datetime, timedelta

# Ensure src module is reachable
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.rag_chain import get_rag_chain
from langchain_core.messages import HumanMessage, AIMessage

from src.database import engine, get_db
from src.models import Draft, Base
from fastapi.responses import StreamingResponse
import json

# Create DB tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Akademik Mevzuat API")

# Setup CORS for local React development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, restrict this to the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Seed Data Function ---
def seed_db(db: Session):
    if db.query(Draft).first() is None:
        mock_drafts = [
            Draft(
                title="Mazeret Sınavı Dilekçesi",
                description="COM-202 Veritabanı Yönetim Sistemleri dersi için sağlık raporuna dayalı detaylı mazeret sınavı başvuru taslağı.",
                status="ready",
                progress=100,
                updated_at=datetime.utcnow() - timedelta(hours=2)
            ),
            Draft(
                title="Ders Muafiyet Başvurusu",
                description="Önceki kurumdan alınan 3 giriş seviyesi kredisi için ders muafiyeti.",
                status="drafting",
                progress=75
            ),
            Draft(
                title="Erasmus Başvuru Dilekçesi",
                description="Güz dönemi öğrenim hareketliliği başvurusu.",
                status="archived",
                progress=100,
                updated_at=datetime.utcnow() - timedelta(days=180)
            ),
            Draft(
                title="Staj Muafiyet Formu",
                description="Yaz dönemi zorunlu staj muafiyeti.",
                status="finalized",
                progress=100,
                updated_at=datetime.utcnow() - timedelta(days=184)
            ),
            Draft(
                title="Yatay Geçiş Başvurusu",
                description="Merkezi yerleştirme puanı (Ek Madde-1) ile yatay geçiş.",
                status="review",
                progress=100,
                updated_at=datetime.utcnow() - timedelta(days=186)
            ),
        ]
        
        # Ekstra taslaklar (Toplamı 12 yapmak için)
        for i in range(6, 13):
            mock_drafts.append(
                Draft(
                    title=f"Eski Taslak {i}",
                    description="Tamamlanmamış veya iptal edilmiş taslak.",
                    status="archived",
                    progress=10
                )
            )
        db.add_all(mock_drafts)
        db.commit()

# Run seed on startup
@app.on_event("startup")
def startup_event():
    db = next(get_db())
    seed_db(db)

# --- Endpoints ---

class Message(BaseModel):
    role: str # "user" or "assistant"
    content: str

class ChatRequest(BaseModel):
    message: str
    history: list[Message] = []

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    rag_chain = get_rag_chain()
    if not rag_chain:
        raise HTTPException(status_code=500, detail="RAG zinciri başlatılamadı. Lütfen veritabanının hazır olduğundan emin olun.")

    chat_history = []
    for msg in req.history:
        if msg.role == "user":
            chat_history.append(HumanMessage(content=msg.content))
        else:
            chat_history.append(AIMessage(content=msg.content))

    try:
        response = rag_chain.invoke({
            "input": req.message,
            "chat_history": chat_history
        })
        
        answer = response["answer"]
        source_docs = []
        for doc in response.get("context", []):
            source_docs.append({
                "source": doc.metadata.get("source", "Bilinmiyor"),
                "page": doc.metadata.get("page", "?"),
                "content": doc.page_content[:200] + "..."
            })
            
        return {
            "answer": answer,
            "sources": source_docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats(db: Session = Depends(get_db)):
    total = db.query(Draft).count()
    ready = db.query(Draft).filter(Draft.status == "ready").count()
    review = db.query(Draft).filter(Draft.status == "review").count()
    
    # Calculate AI Efficiency: Simple mock metric (94 + up to 5 based on some ratio)
    # Just to show dynamic but high number
    ai_efficiency = 90 + min(total, 9)
    
    return {
        "total": total,
        "ready": ready,
        "review": review,
        "efficiency": ai_efficiency
    }

@app.get("/api/drafts")
async def get_drafts(db: Session = Depends(get_db)):
    drafts = db.query(Draft).order_by(Draft.updated_at.desc()).all()
    
    result = []
    for d in drafts:
        result.append({
            "id": d.id,
            "title": d.title,
            "description": d.description,
            "status": d.status,
            "progress": d.progress,
            "updated_at": d.updated_at.isoformat()
        })
    return result

@app.get("/api/sources")
async def get_sources():
    raw_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
    if not os.path.exists(raw_dir):
        return []
    
    files = []
    for f in os.listdir(raw_dir):
        if f.endswith(('.pdf', '.txt', '.docx')):
            files.append(f)
    return files

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
