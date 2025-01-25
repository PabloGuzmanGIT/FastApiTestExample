from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2 import Error
from typing import List

app = FastAPI()

# Pydantic model to parse the incoming JSON data
class UserData(BaseModel):
    name: str
    age: int
    email: str

# Database connection
conn = psycopg2.connect(dbname="TestApiConect", user="postgres", password="petizo", host="localhost", port='5432')
cur = conn.cursor()

# Endpoint to store the data in the database
@app.post("/store-data/")
async def store_data(data: UserData):  # Use the UserData Pydantic model
    try:
        # Create table if it doesn't exist
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                age INT,
                email VARCHAR(100)
            )
        """)
        conn.commit()

        # Insert the received data into the table
        cur.execute(
            "INSERT INTO users (name, age, email) VALUES (%s, %s, %s)",
            (data.name, data.age, data.email),
        )
        conn.commit()
        cur.execute("SELECT * FROM users WHERE name = %s", (data.name,))
        stored_data = cur.fetchall()

        print("Stored Data:", stored_data)
        return {"message": "Data stored successfully", "data": data}

    except Error as e:
        # Log and include the error message in the response for debugging purposes
        print(f"Error occurred: {str(e)}")  # Print error to the console or log file
        raise HTTPException(status_code=500, detail=f"Error inserting data: {str(e)}")


# Endpoint to fetch data
@app.get("/get-data/", response_model=List[UserData])
async def get_data():
    try:
        # Query to get data from the users table
        cur.execute("SELECT name, age, email FROM users")
        rows = cur.fetchall()

        # Convert the result to a list of dictionaries
        users = []
        for row in rows:
            user = UserData(name=row[0], age=row[1], email=row[2])
            users.append(user)

        return users
    except Error as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")



