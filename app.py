from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
import mysql.connector.pooling
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os
from typing import List, Tuple, Dict, Optional
import json

app=FastAPI()

# Get database credentials from environment variables
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')

# Database configuration
dbconfig = {
    "host": DB_HOST,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME
}

# Initialize connection pool
conn_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)
print("Connected to MySQL database")

# Function to get a connection from the pool
def get_connection():
    return conn_pool.get_connection()

# Function to execute queries
def execute_query(query: str, params: Tuple = (), commit: bool = False) -> List[dict]:
    con = get_connection()
    cursor = con.cursor(dictionary=True)
    cursor.execute(query, params)
    
    result = None
    if not commit:
        result = cursor.fetchall()
    else:
        con.commit()
        
    cursor.close()
    con.close()
    return result

def get_db_attrs_with_imgs() -> List[dict]:
    attractions_query = "SELECT * FROM attractions"
    images_query = "SELECT url FROM images WHERE attraction_id = %s"
    
    attractions = execute_query(attractions_query)
    
    for attraction in attractions:
        attraction_id = attraction["id"]
        image_records = execute_query(images_query, (attraction_id,))
        attraction["images"] = [record["url"] for record in image_records]
       
    return attractions

def get_db_attr_with_imgs(attractionId):
    query = "SELECT * FROM attractions WHERE id = %s"
    images_query = "SELECT url FROM images WHERE attraction_id = %s"
    
    # First, attempt to fetch the attraction
    attraction_result = execute_query(query, (attractionId,))
    
    # Check if the result is not empty
    if attraction_result:
        # If the attraction exists, proceed to fetch its images
        attraction = attraction_result[0]
        image_records = execute_query(images_query, (attraction["id"],))
        if image_records:  # Check if there are any image records
            attraction["images"] = [record["url"] for record in image_records]
        
        return attraction
    else:
        raise CustomHTTPException(status_code=400, detail={"error": True,"message": "景點編號不正確"})

def get_db_mrts() -> List[str]:
    query = """
    SELECT mrt 
    FROM (
        SELECT mrt, COUNT(*) as frequency 
        FROM attractions 
        GROUP BY mrt
    ) AS mrt_counts 
    ORDER BY frequency DESC
    """
    result = execute_query(query)
    
    # Extracting the 'mrt' values from the result
    mrt_values = [row['mrt'] for row in result]
    
    return mrt_values

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        return JSONResponse(status_code=404, content={"data": None})
    else:
        return JSONResponse(status_code=exc.status_code, content={"error": "True400"})

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": "validation_exception_handler"})

@app.exception_handler(Exception)  # Add this handler for general exceptions
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": True, "message": "Internal server error"},
    )
    
class CustomHTTPException(HTTPException):
    def __init__(self, status_code, detail=None, headers=None):
        super().__init__(status_code, detail, headers)

    def __str__(self):
        # Convert the detail dictionary to a JSON string
        return json.dumps(self.detail)
      
@app.exception_handler(CustomHTTPException)
async def custom_http_exception_handler(request: Request, exc: CustomHTTPException):
    # Directly return a JSONResponse with the desired structure
    # No need to parse exc.detail with json.loads() since it's already a string
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.detail  # Use exc.detail directly
    )

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")

@app.get("/api/attractions", response_class=JSONResponse)
async def get_attractions(
    request: Request, 
    page: int = Query(..., ge=0), 
    size: int = Query(12, ge=1),
    keyword: Optional[str] = Query(None)
):
    attractions = get_db_attrs_with_imgs()

    # Debugging: Print the keyword
    if keyword:
        print(f"Received keyword: {keyword}")

    # Filter by keyword in attraction name if provided
    if keyword:
        keyword_utf8 = keyword.encode('utf-8').decode('utf-8')  # Ensure keyword is treated as UTF-8 string
        filtered_attractions = [attr for attr in attractions if keyword_utf8 in attr["name"] or keyword_utf8 == attr.get["mrt"]]
    else:
        filtered_attractions = attractions

    # Debugging: Print the filtered attractions
    print(f"Filtered attractions: {filtered_attractions}")

    # Pagination logic
    start = page * size
    end = start + size
    paginated_attractions = filtered_attractions[start:end]

    return JSONResponse(status_code=200, content=paginated_attractions)
  
@app.get("/api/attraction/{attractionId}", response_class=JSONResponse)
async def get_attr(request: Request, attractionId: Optional[int] = None):
  if attractionId:
    data = get_db_attr_with_imgs(attractionId)
    print (data)
    return JSONResponse(status_code=200,content=data)
  
@app.get("/api/mrts", response_class = JSONResponse)
async def get_mrts(request: Request):
  data = get_db_mrts()
  return JSONResponse(status_code=200,content={"data": data})