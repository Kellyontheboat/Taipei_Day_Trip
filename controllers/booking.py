from fastapi import APIRouter, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from models.booking import BookingWrapper
from models.members import UserLogin, CurrentMember
from models.booking import BookingWrapper, BookingResponse, Booking, get_booking_from_db
from models.redis.r_booking import retrieve_booking_data_redis, store_booking_data_redis, delete_booking_data_redis
from exceptions import CustomHTTPException
from starlette.requests import Request

from models.booking import add_booking_into_db
from controllers.member import get_current_member

from models.booking import BookingWrapper, BookingData, Attraction, delete_booking_from_db
from typing import List
import logging

router = APIRouter()

#???應該要區分一個是沒有權限一個是booking Data沒有完全填寫 或是內容有誤
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
          
        #??分清楚傳遞的變數格式
        booking = Booking(**booking_dt)
        booking_id = add_booking_into_db(booking)
        
        booking_redis = {
            'data': {
                'id': booking_id,  # booking.id should be set after DB insertion
                'attraction': {
                    'id': booking_info.attraction.id,
                    'name': booking_info.attraction.name,
                    'address': booking_info.attraction.address,
                    'image': str(booking_info.attraction.image)  # Convert Url to string
                },
                'date': booking_info.date,
                'time': booking_info.time,
                'price': booking_info.price
            }
        }
        print(user)
        member_id = user.get('id')
        store_booking_data_redis(member_id, booking_redis)
        print(f"post /api/booking{booking_data}")
        return booking_data
    except ValueError as e:
        logging.error(f"ValueError: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except RequestValidationError as e:
        logging.error(f"RequestValidationError: {e.errors()}")
        raise HTTPException(status_code=422, detail="Validation error")
    except CustomHTTPException as e:
        logging.error(f"CustomHTTPException: {e}")
        raise e
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
      
@router.get("/api/booking", response_model=BookingResponse)
async def fetch_bookings(user: dict = Depends(get_current_member)):
    #print (user)
    try:
        member_id = user.get('id')
            
        print(member_id)
        bookings_from_redis = retrieve_booking_data_redis(member_id)
        print(f'retrieve_booking_data_redis${bookings_from_redis}')

        if bookings_from_redis:
            return bookings_from_redis
        else:
            # Fetch bookings from database if not found in Redis
            bookings_from_db = get_booking_from_db(member_id) 
            #{'bookings': booking_data,'total_cost': total_cost}
            store_booking_data_redis(member_id, bookings_from_db)
            return bookings_from_db

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/booking/{booking_id}")
async def delete_booking(booking_id: int, user: dict = Depends(get_current_member)):
    member_id = user.get('id')

    # Delete from SQL Database
    db_response = delete_booking_from_db(booking_id)
    
    if db_response.get("success"):
        # Delete from Redis
        redis_response = delete_booking_data_redis(member_id, booking_id)
        if redis_response.get("success"):
            return {"success": True, "message": "Booking deleted successfully from DB and Redis."}
        else:
            return {"success": False, "message": redis_response.get("message")}
    else:
        raise HTTPException(status_code=500, detail="Failed to delete booking from DB.")