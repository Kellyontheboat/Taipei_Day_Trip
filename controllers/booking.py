from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from models.booking import BookingWrapper
from models.members import UserLogin, CurrentMember
from models.booking import BookingWrapper, BookingResponse, Booking, get_booking_from_db
#from models.redis.r_booking import retrieve_booking_data_redis, store_booking_data_redis, delete_booking_data_redis
from exceptions import CustomHTTPException
from starlette.requests import Request

from controllers.member import get_current_member

from models.booking import BookingWrapper, BookingData, Attraction, delete_booking_from_db, add_booking_into_db

from typing import List
import logging

router = APIRouter()

@router.post("/api/booking", response_model=BookingWrapper)
async def create_booking(booking_data: BookingWrapper, user: dict = Depends(get_current_member)):
    try:
        # Convert user dictionary to UserLogin object
        user_obj = CurrentMember(**user)        
        booking_info = booking_data.data
        
        # Add booking to the database
        # Pass the Booking instance to the function
        booking_dt = {
            "attraction_id": booking_info.attraction.id,
            "date": booking_info.date,
            "time": booking_info.time,
            "price": booking_info.price,
            "member_id": user_obj.id
        } 
        
        booking = Booking(**booking_dt)
        add_booking_response = add_booking_into_db(booking)
        
        if add_booking_response.get("success"):
            return booking_data
        
        else:
            raise HTTPException(status_code=500, detail="Failed to add booking into DB.")
        
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")

@router.get("/api/booking", response_model=BookingResponse)
async def fetch_bookings(user: dict = Depends(get_current_member)):
    try:
        member_id = user.get('id')
        bookings_from_db = get_booking_from_db(member_id) 
        
        return bookings_from_db

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/booking/{booking_id}")
async def delete_booking(booking_id: int, user: dict = Depends(get_current_member)):
    member_id = user.get('id')

    # Delete from SQL Database
    db_response = delete_booking_from_db(booking_id)
    
    if db_response.get("success"):
        return {"success": True, "message": "Booking deleted successfully from DB."}
        
    else:
        raise HTTPException(status_code=500, detail="Failed to delete booking from DB.")