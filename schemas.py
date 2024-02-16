from pydantic import BaseModel

class Contact(BaseModel):
    contact_id: int
    email_address: str
    country: str
    customer_date: str

class DecisionResponse(BaseModel):
    sync_action: str
