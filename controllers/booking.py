from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from fastapi.responses import JSONResponse
from models.booking import BookingWrapper
from models.members import UserLogin, CurrentMember
from models.booking import BookingWrapper, BookingWrapperWithId, Booking, get_booking_from_db
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
            
        booking = Booking(**booking_dt)
        add_booking_into_db(booking)

        return booking_data
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
      
@router.get("/api/booking", response_model=List[BookingWrapperWithId])
async def fetch_bookings(user: dict = Depends(get_current_member)):
    try:
        member_id = user.get('id')
        return get_booking_from_db(member_id)
        #[{'data': {'attraction': {'id': 6, 'name': '陽明山溫泉區', 'address': '臺北市  北投區竹子湖路1之20號', 'image': 'https://www.travel.taipei/d_upload_ttn/sceneadmin/pic/11000985.jpg'}, 'date': '2024-06-15', 'time': 'afternoon', 'price': 2000}}, {'data': {'attraction': {'id': 14, 'name': '中正紀念堂', 'address': '臺北市  中正區中山南路21號', 'image': 'https://www.travel.taipei/d_upload_ttn/sceneadmin/pic/11000375.jpg'}, 'date': '2024-06-17', 'time': 'morning', 'price': 2500}}]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/api/booking/{booking_id}", response_model=dict)
async def delete_booking(booking_id: int, user: dict = Depends(get_current_member)):
    response = delete_booking_from_db(booking_id)
    if response["success"]:
        return {"message": "Booking deleted successfully"}
    else:
        raise HTTPException(status_code=500, detail=response["error"])


# data=BookingData(attraction=Attraction(id=4, name='國立故宮博物院', address='臺北市  士林區至善路二段221號', image=Url('https://www.travel.taipei/d_upload_ttn/sceneadmin/image/A0/B0/C0/D14/E810/F21/48d66fbd-1ba3-4efd-837a-3767db5f52e0.jpg')), date='2024-06-20', time='afternoon', price=2000)
# INFO:root:Booking Info: attraction=Attraction(id=4, name='國立故宮博物院', address='臺北市  士林區至善路二段221號', image=Url('https://www.travel.taipei/d_upload_ttn/sceneadmin/image/A0/B0/C0/D14/E810/F21/48d66fbd-1ba3-4efd-837a-3767db5f52e0.jpg')) date='2024-06-20' time='afternoon' price=2000
# ERROR:root:Unexpected error: 'dict' object has no attribute 'id'
# INFO:     127.0.0.1:55426 - "POST /api/booking HTTP/1.1" 500 Internal Server Error