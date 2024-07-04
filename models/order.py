from pydantic import BaseModel, HttpUrl

#from models.booking import Attraction
class Attraction(BaseModel):
    name: str
    address: str
    image: HttpUrl
    
class Trip(BaseModel):
    attraction: Attraction
    date: str
    time: str

class Contact(BaseModel):
    name: str
    email: str
    phone: str

class Order(BaseModel):
    price: int
    trip: Trip
    contact: Contact

class OrderRequest(BaseModel):
    prime: str
    order: Order

class PaymentResponse(BaseModel):
    status: int
    message: str

class OrderResponse(BaseModel):
    number: str
    payment: PaymentResponse
    


