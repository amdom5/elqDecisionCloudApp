from sqlalchemy.orm import Session
from . import models

def get_country_rule(db: Session, country_name: str):
    return db.query(models.CountryList).filter(models.CountryList.country == country_name).first()
