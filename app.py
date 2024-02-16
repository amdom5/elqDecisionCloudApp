from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from . import crud, models, schemas, database
from .eloqua_oauth_fastapi import get_current_user

app = FastAPI()

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/decision/", response_model=schemas.DecisionResponse)
def decision_service(contact: schemas.Contact, db: Session = Depends(get_db), user: str = Depends(get_current_user)):
    country_rule = crud.get_country_rule(db, contact.country)
    sync_action = "Yes" if country_rule and country_rule.rule == "SpecificRule" else "No"
    return {"sync_action": sync_action}
