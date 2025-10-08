from fastapi import APIRouter, HTTPException, Depends
from app.services.ai_adapter import text_classifier
from app.services.db import get_db, create_dispute, get_dispute, list_disputes, update_dispute
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix="/disputes", tags=["disputes"])

class DisputeRequest(BaseModel):
    narrative: str

class DisputeBatchRequest(BaseModel):
    narratives: List[str]

class DisputeResponse(BaseModel):
    id: str
    narrative: str
    classification: str | None = None
    classification_confidence: float | None = None
    created_at: str | None = None

class RetrainRequest(BaseModel):
    texts: List[str]
    labels: List[int]

class EvaluateRequest(BaseModel):
    texts: List[str]
    labels: List[int]

class EvaluateResponse(BaseModel):
    accuracy: float

@router.post("/classify", response_model=DisputeResponse)
def classify_dispute(req: DisputeRequest, db: Session = Depends(get_db)):
    try:
        prediction = text_classifier.predict([req.narrative])[0]
        # For demo, use string label
        label = "dispute" if prediction == 1 else "not_dispute"
        dispute = create_dispute(db, req.narrative, label, 1.0)
        return DisputeResponse(
            id=dispute.id,
            narrative=dispute.narrative,
            classification=dispute.classification,
            classification_confidence=dispute.classification_confidence,
            created_at=str(dispute.created_at)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/classify/batch", response_model=List[int])
def classify_batch(req: DisputeBatchRequest):
    try:
        return text_classifier.predict(req.narratives)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/retrain")
def retrain_model(req: RetrainRequest):
    try:
        text_classifier.retrain(req.texts, req.labels)
        return {"status": "retrained"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/evaluate", response_model=EvaluateResponse)
def evaluate_model(req: EvaluateRequest):
    try:
        metrics = text_classifier.evaluate(req.texts, req.labels)
        return EvaluateResponse(**metrics)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/model/health")
def model_health():
    return {"healthy": text_classifier.is_healthy()}

@router.get("/", response_model=list[DisputeResponse])
def get_all_disputes(db: Session = Depends(get_db)):
    disputes = list_disputes(db)
    return [DisputeResponse(
        id=d.id,
        narrative=d.narrative,
        classification=d.classification,
        classification_confidence=d.classification_confidence,
        created_at=str(d.created_at)
    ) for d in disputes]

@router.get("/{dispute_id}", response_model=DisputeResponse)
def get_one_dispute(dispute_id: str, db: Session = Depends(get_db)):
    d = get_dispute(db, dispute_id)
    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return DisputeResponse(
        id=d.id,
        narrative=d.narrative,
        classification=d.classification,
        classification_confidence=d.classification_confidence,
        created_at=str(d.created_at)
    )

@router.put("/{dispute_id}", response_model=DisputeResponse)
def update_one_dispute(dispute_id: str, req: DisputeRequest, db: Session = Depends(get_db)):
    d = update_dispute(db, dispute_id, narrative=req.narrative)
    if not d:
        raise HTTPException(status_code=404, detail="Dispute not found")
    return DisputeResponse(
        id=d.id,
        narrative=d.narrative,
        classification=d.classification,
        classification_confidence=d.classification_confidence,
        created_at=str(d.created_at)
    )
