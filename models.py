from sqlalchemy import Column, Integer, String
from database import Base

class CountryList(Base):
    __tablename__ = "countrylist"
    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String)
    rule = Column(String)
