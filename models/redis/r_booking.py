# from fastapi import APIRouter, Depends, HTTPException
# import redis
# import os
# import json

# REDIS_HOST = os.getenv('REDIS_HOST')
# REDIS_PORT = os.getenv('REDIS_PORT', '6379')
# REDIS_DB = os.getenv('REDIS_DB', '0')

# redis_client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)

# import logging

# logging.basicConfig(level=logging.DEBUG)

# # test redis connection
# try:
#     redis_client.ping()
#     print("Connected to Redis")
# except redis.ConnectionError as e:
#     print(f"Connection error: {e}")

# redis_client.set('my_key', 'my_value')
# value = redis_client.get('my_key')
# print(value)  # Output: b'my_value'

# def store_booking_data_redis(member_id, new_booking):
#     """ Store booking data in Redis """
#     redis_key = f"member:{member_id}"
#     existing_data = redis_client.get(redis_key)
    
#     if not redis_client.exists(redis_key):
#         bookings = []
#         total_cost = 0
#     else:
#         existing_data = json.loads(existing_data)
#         bookings = existing_data.get('bookings', [])
#         total_cost = existing_data.get('total_cost', 0)
    
#     if 'bookings' in new_booking:  # Rendering booking page
#         bookings = new_booking['bookings']
#         total_cost = new_booking['total_cost']
#     else:  # Post new booking scenario
#         booking_data = new_booking
#         bookings.append(booking_data)
#         total_cost += booking_data['data']['price']
    
#     # Store the updated data back in Redis
#     updated_data = {
#         'bookings': bookings,
#         'total_cost': total_cost
#     }

#     redis_client.set(redis_key, json.dumps(updated_data))
    
# def retrieve_booking_data_redis(member_id):
#     """ Retrieve booking data from Redis """
#     redis_key = f"member:{member_id}"
#     # Check if the key exists in Redis
#     if not redis_client.exists(redis_key):
#         return None
    
#     bookings_json = redis_client.get(redis_key) #redis result is a byte string $b'{"bookings": [], "total_cost": 0}'
    
#     print(f'retrieve_booking_data_redis ${bookings_json}')
#     # Decode the byte string to a regular string/no need
#     #bookings_json = bookings_json.decode('utf-8')
    
#     #Parse the JSON string to a dictionary
#     booking_data = json.loads(bookings_json)

#     # Check if the bookings are empty
#     if not booking_data['bookings']:
#         return {
#             'bookings': [],
#             'total_cost': 0
#         }
        
#     # Sort bookings by id in descending order
#     booking_data['bookings'].sort(key=lambda x: x['data']['id'], reverse=True)
    
#     # container
#     formatted_data = {
#         'bookings': [],
#         'total_cost': 0
#     }
#     total_cost = 0

#     # store data into container
#     bookings = booking_data['bookings']

#     for booking in bookings: #[{}.{}.{}...]
#         formatted_data['bookings'].append({
#             'data': {
#                 'id': booking['data']['id'],
#                 'attraction': booking['data']['attraction'],
#                 'date': booking['data']['date'],
#                 'time': booking['data']['time'],
#                 'price': booking['data']['price'],
#             }
#         })
#         total_cost += booking['data']['price']
    
#     formatted_data['total_cost'] = total_cost
    
#     return formatted_data

# def delete_booking_data_redis(member_id, booking_id):

#     redis_key = f"member:{member_id}"
#     try:
#         if not redis_client.exists(redis_key):
#             return #if the first time render DB data and delete
        
#         # Retrieve existing booking data
#         booking_data = redis_client.get(redis_key)
#         if booking_data:
#             booking_data = json.loads(booking_data)
            
#             if booking_id is None:
#                 # If booking_id is None, clear all bookings for the member
#                 updated_bookings = []
#                 total_cost = 0
                
#             else:
#                 # Filter out the booking to be deleted
#                 updated_bookings = [booking for booking in booking_data['bookings'] if booking['data']['id'] != booking_id]
#                 total_cost = sum(booking['data']['price'] for booking in updated_bookings)
            
#             # Create the updated data structure
#             updated_data = {
#                 'bookings': updated_bookings,
#                 'total_cost': total_cost
#             }
            
#             redis_client.set(redis_key, json.dumps(updated_data))
            
#             if booking_id is None:
#                 print(f"All bookings deleted successfully from Redis for member ID {member_id}.")
#             else:
#                 print(f"Booking with ID {booking_id} deleted successfully from Redis.")
            
#             return {"success": True}
#         else:
#             print(f"No booking data found in Redis for member ID {member_id}.")
#             return {"success": False, "message": f"No booking data found in Redis for member ID {member_id}."}
    
#     except Exception as e:
#         print(f"Error deleting booking from Redis: {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Error deleting booking from Redis: {str(e)}")