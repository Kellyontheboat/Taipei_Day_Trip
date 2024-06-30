from pydantic import BaseModel, constr, PositiveInt, validator, HttpUrl
from models.attractions import get_db_attr_for_booking
from datetime import datetime
from database import execute_query
import logging


class Attraction(BaseModel):
    id: int
    name: str
    address: str
    image: HttpUrl

class BookingData(BaseModel):
    attraction: Attraction
    date: constr(pattern=r'^\d{4}-\d{2}-\d{2}$')
    time: constr(pattern=r'^(morning|afternoon)$')
    price: PositiveInt
    
class BookingDataWithId(BaseModel):
    id: int
    attraction: Attraction
    date: constr(pattern=r'^\d{4}-\d{2}-\d{2}$')
    time: constr(pattern=r'^(morning|afternoon)$')
    price: PositiveInt

class BookingWrapper(BaseModel):
    data: BookingData
    
class BookingWrapperWithId(BaseModel):
    data: BookingDataWithId
    
class Booking(BaseModel):
    attraction_id: PositiveInt
    date: constr(pattern=r'^\d{4}-\d{2}-\d{2}$')
    time: constr(pattern=r'^(morning|afternoon)$')
    price: PositiveInt
    member_id: PositiveInt
    

    
#??這個加到購物車的資料應該要用pydantic
def add_booking_into_db(booking: Booking):
  
    logging.info(f"AAAAA {booking}")
    logging.info(f"Adding booking to DB for member_id={booking.member_id} at attraction_id={booking.attraction_id}")

    query = """
    INSERT INTO bookings (attraction_id, date, time, price, member_id, created_at)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    
    try:
        execute_query(
            query,
            (booking.attraction_id, booking.date, booking.time, booking.price, booking.member_id, datetime.now()),
            commit=True
        )
        logging.info("Booking successfully added to the database.")
    except Exception as e:
        logging.error(f"Failed to add booking to DB: {e}")
        raise
      
#??拿到屬於自己token的data ，所以需要用到出來的資料需要符合BookingData的格式
#??get_db_attr_with_imgs思考是否要新建立一個是只拿render booking需要的資料
def get_booking_from_db(member_id):
    bookings_query =  """
      SELECT id, attraction_id, date, time, price 
      FROM bookings 
      WHERE member_id = %s 
      ORDER BY created_at DESC
    """
    bookings = execute_query(bookings_query, (member_id,))
    # [{'attraction_id': 6, 'date': datetime.date(2024, 6, 15), 'time': 'afternoon', 'price': 2000}, {'attraction_id': 14, 'date': datetime.date(2024, 6, 17), 'time': 'morning', 'price': 2500}]
    booking_data = []
    for booking in bookings:
        attraction_id = booking['attraction_id']
        attraction_info = get_db_attr_for_booking(attraction_id)
        booking_data.append({
            'data': {
                'id': booking['id'],
                'attraction': attraction_info,
                'date': booking['date'].strftime('%Y-%m-%d'),
                'time': booking['time'],
                'price': booking['price'],
            }
        })
    return booking_data
    #[{'data': {'attraction': {'id': 6, 'name': '陽明山溫泉區', 'address': '臺北市  北投區竹子湖路1之20號', 'image': 'https://www.travel.taipei/d_upload_ttn/sceneadmin/pic/11000985.jpg'}, 'date': '2024-06-15', 'time': 'afternoon', 'price': 2000}}, {'data': {'attraction': {'id': 14, 'name': '中正紀念堂', 'address': '臺北市  中正區中山南路21號', 'image': 'https://www.travel.taipei/d_upload_ttn/sceneadmin/pic/11000375.jpg'}, 'date': '2024-06-17', 'time': 'morning', 'price': 2500}}]
  
def delete_booking_from_db(booking_id):
    print("Attempting to delete booking with ID:", booking_id)
    delete_query = """
        DELETE FROM bookings
        WHERE id = %s
    """
    try:
        execute_query(delete_query, (booking_id,), commit=True)
        print("Booking deleted successfully from DB.")
        return {"success": True}
    except Exception as e:
        print("Error deleting booking from DB:", str(e))
        return {"success": False, "error": str(e)}
