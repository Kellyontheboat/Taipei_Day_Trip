from pydantic import BaseModel, HttpUrl
from models.redis.r_booking import retrieve_booking_data_redis, store_booking_data_redis, delete_booking_data_redis
from models.booking import get_booking_from_db
from typing import Optional, List
from database import execute_query
from enum import Enum
import logging

from fastapi import HTTPException

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
    #order: Order
    contact: Contact
    memberId: int

class PaymentResponse(BaseModel):
    status: int
    message: str

class OrderResponse(BaseModel):
    number: str
    payment: PaymentResponse

class PayStatus(str, Enum):
    PAID = 'PAID'
    UNPAID = 'UNPAID'
    
class OrderData(BaseModel):
    member_id: int
    order_number: str
    pay_status: PayStatus
    total_cost: int
    rec_trade_id: Optional[str] = None
    
class UpdateOrder(BaseModel):  # Update after TapPay process
    order_number: str
    pay_status: PayStatus
    rec_trade_id: str  # Make rec_trade_id required
    
def save_order_into_db(order_data: OrderData):
    try:
        # Insert order into database
        insert_query = """
            INSERT INTO orders (order_number, member_id, total_price, rec_trade_id, pay_status)
            VALUES (%s, %s, %s, %s, %s)
        """
        params = (
            order_data.order_number,
            order_data.member_id,
            order_data.total_cost,
            order_data.rec_trade_id,
            order_data.pay_status
        )
        # Execute the INSERT query
        execute_query(insert_query, params, commit=True)
        
        # Retrieve the auto-generated order_id after insertion
        order_id_query = "SELECT id FROM orders WHERE order_number = %s"
        result = execute_query(order_id_query,(order_data.order_number,))
        order_id = result[0]['id']
        return True, order_id
        
    except Exception as e:
        print(f"Error saving order into DB: {str(e)}")
        return False, None
    
def update_order_status_db(update_order: UpdateOrder):
    try:
        query = """
            UPDATE orders
            SET pay_status = %s, rec_trade_id = %s
            WHERE order_number = %s
        """
        
        execute_query(query, (update_order.pay_status, update_order.rec_trade_id, update_order.order_number),commit=True)
        
        # Log success message
        logging.info(f"Order {update_order.order_number} status updated successfully.")

    except Exception as e:
        # Handle other unexpected errors
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while updating order status.")

def save_booking_into_order_schedule_db(member_id: int, order_id: int):
    try:
        # Fetch booking data from Redis
        booking_data = retrieve_booking_data_redis(member_id)
        print(f'save_booking_into_order_schedule_db ${booking_data}')
        bookings = booking_data['bookings']

        # Save each booking item into the order_schedules table
        for booking in bookings:
            booking_data = booking['data']
            query = """
                INSERT INTO order_schedules (order_id, attraction_id, date, time, price)
                VALUES (%s, %s, %s, %s, %s)
            """
            execute_query(query, (order_id, booking_data['attraction']['id'], booking_data['date'], booking_data['time'], booking_data['price']), commit=True)

        logging.info(f"Booking data saved into order_schedules for member_id: {member_id}")

    except Exception as e:
        logging.error(f"Unexpected error when saving booking data: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while saving booking data into order_schedules.")
    
def delete_booking_data_db(member_id: int):
    try:
        query = """
            DELETE FROM bookings WHERE member_id = %s
        """
        execute_query(query, (member_id,), commit=True)

        logging.info(f"Booking data deleted for member_id: {member_id}")

    except Exception as e:
        logging.error(f"Unexpected error when deleting booking data: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred while deleting booking data.")