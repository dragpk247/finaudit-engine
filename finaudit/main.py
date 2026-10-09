from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import os

from finaudit.parsers import TransactionParser
from finaudit.auditor import SpendAuditor
from finaudit.ai_router import ai_router

app = FastAPI(
    title="FinAudit Engine",
    description="Hybrid AI SaaS & Bank Statement Audit API",
    version="0.1.0"
)

STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h1>FinAudit Engine Running</h1><p>Visit <a href='/docs'>/docs</a> for API</p>")

@app.get("/api/health")
async def health():
    status = await ai_router.check_health()
    return {"status": "ok", "inference_tiers": status}

@app.post("/api/audit/csv")
async def audit_csv(file: UploadFile = File(...)):
    """Ingests a CSV bank/credit card export and runs full quantitative & AI audit."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only .csv files are supported")
    
    content_bytes = await file.read()
    content_str = content_bytes.decode("utf-8", errors="ignore")
    
    transactions = TransactionParser.parse_csv(content_str)
    if not transactions:
        raise HTTPException(status_code=400, detail="No valid transactions parsed from CSV. Check column headers.")
    
    stats = SpendAuditor.analyze_transactions(transactions)
    report = await SpendAuditor.generate_ai_report(stats)
    return report

class NegotiateRequest(BaseModel):
    merchant: str
    current_price: float
    old_price: float

@app.post("/api/negotiate")
async def draft_negotiation(req: NegotiateRequest):
    """Generates a tailored vendor cancellation/price rollback email."""
    prompt = f"Draft a firm, professional price-rollback or cancellation email to {req.merchant}. They increased their fee from ${req.old_price} to ${req.current_price}. Demand to be returned to the grandfathered rate or process a cancellation immediately."
    email_text = await ai_router.generate(prompt)
    return {"merchant": req.merchant, "email_template": email_text}
