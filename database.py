import os
import mysql.connector.pooling

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
def execute_query(query: str, params: tuple = (), commit: bool = False) -> list:
    try:
        con = get_connection()
        cursor = con.cursor(dictionary=True)
        cursor.execute(query, params)

        result = None
        if not commit:
            result = cursor.fetchall()
            print(f"Query result: {result}")
        else:
            con.commit()

        cursor.close()
        con.close()
        return result
    except Exception as e:
        print(f"Query execution error: {str(e)}")
        raise
