from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Event, Validation, Analysis
from app.services.ml import train

router=APIRouter(prefix="/admin",tags=["Admin / ML"])

@router.get("/model/status")
def model_status():
    p=Path("./artifacts/xgboost.joblib"); return {"available":p.exists(),"path":str(p)}

@router.post("/model/train")
def model_train(db:Session=Depends(get_db)):
    rows=[]
    for v in db.query(Validation).all():
        if v.label=="UNCERTAIN": continue
        a=db.query(Analysis).filter(Analysis.event_id==v.event_id).first()
        if not a: continue
        rows.append({**a.payload.get("features",{}),"label":v.label})
    try:
        return {"ok":True,**train(rows,"./artifacts/xgboost.joblib")}
    except ValueError as exc:
        raise HTTPException(400,str(exc))
