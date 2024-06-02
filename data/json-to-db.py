import json
import mysql.connector.pooling
import re
import os
from typing import List, Tuple

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

# Function to create the attractions and images tables
def create_tables():
    create_attractions_query = """
        CREATE TABLE IF NOT EXISTS attractions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            category VARCHAR(255),
            description TEXT,
            address TEXT,
            direction TEXT,
            mrt VARCHAR(255),
            lat FLOAT(9, 6),
            lng FLOAT(9, 6)
        )
    """
    
    create_images_query = """
        CREATE TABLE IF NOT EXISTS images (
            id INT AUTO_INCREMENT PRIMARY KEY,
            attraction_id INT,
            url TEXT,
            FOREIGN KEY (attraction_id) REFERENCES attractions(id)
        )
    """
    
    execute_query(create_attractions_query, commit=True)
    execute_query(create_images_query, commit=True)

# Function to insert attraction data
def insert_attraction(attraction: dict) -> int:
    query = """
        INSERT INTO attractions (
            id, name, category, description, address, direction, mrt, lat, lng
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    
    data_attraction = (
        attraction["_id"], attraction["name"], attraction["CAT"], attraction["description"],
        attraction["address"], attraction["direction"], attraction["MRT"],
        float(attraction["latitude"]), float(attraction["longitude"])
    )
    
    execute_query(query, data_attraction, commit=True)
    return attraction["_id"]

# Function to insert image data
def insert_images(attraction_id: int, image_urls: List[str]):
    query = """
        INSERT INTO images (attraction_id, url) VALUES (%s, %s)
    """
    
    for url in image_urls:
        execute_query(query, (attraction_id, url), commit=True)

# Function to get attractions from the database and their images
def get_attractions() -> List[dict]:
    attractions_query = "SELECT * FROM attractions"
    images_query = "SELECT url FROM images WHERE attraction_id = %s"
    
    attractions = execute_query(attractions_query)
    
    for attraction in attractions:
        attraction_id = attraction["id"]
        image_records = execute_query(images_query, (attraction_id,))
        attraction["images"] = [record["url"] for record in image_records]
       
    return attractions

# Function to split concatenated URLs
def split_urls(concatenated_urls: str) -> List[str]:
    # Add a space before each 'http' or 'https' to properly split the URLs
    spaced_urls = re.sub(r'(https?://)', r' \1', concatenated_urls)
    # Split the string into a list of URLs
    urls = spaced_urls.split()
    return urls

# Main function
def main():
    # Load JSON data
    with open('taipei-attractions.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    create_tables()
    
    for attraction in data["result"]["results"]:
        attraction_id = insert_attraction(attraction)
        
        # Split and filter image URLs
        concatenated_urls = attraction["file"]
        image_urls = split_urls(concatenated_urls)
        valid_image_urls = [url for url in image_urls if re.search(r'\.(jpg|jpeg|png)$', url, re.IGNORECASE)]
        
        insert_images(attraction_id, valid_image_urls)
    
    # Get and print attractions from the database
    attractions = get_attractions()

if __name__ == "__main__":
    main()

