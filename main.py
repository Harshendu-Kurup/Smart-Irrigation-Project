import sys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from sqlalchemy import create_engine
from pymongo import MongoClient

# ===================================================================
# --- 1. SETTINGS & APP INITIALIZATION ---
# ===================================================================

app = FastAPI()

# --- CORS Middleware (This is the fix from earlier) ---
origins = [
    "http://localhost:3000",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===================================================================
# --- 2. DATABASE CONNECTIONS ---
# ===================================================================

# --- PostgreSQL Connection ---
pg_user = 'postgres'
pg_password = 'H%40rshendu12'  # Your URL-encoded password
pg_port = '5432'
pg_db = 'iot_assignment'
pg_host = 'localhost'

try:
    pg_engine = create_engine(f'postgresql://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_db}')
    print("Successfully connected to PostgreSQL.")
except Exception as e:
    print(f"--- POSTGRESQL CONNECTION ERROR ---")
    print(f"Error: {e}")
    pg_engine = None

# --- MongoDB Connection ---
try:
    mongo_client = MongoClient('mongodb://localhost:27017/')
    mongo_client.server_info() # Test connection
    mongo_db = mongo_client['iot_assignment_db']
    print("Successfully connected to MongoDB.")
except Exception as e:
    print(f"--- MONGODB CONNECTION ERROR ---")
    print(f"Error: {e}")
    mongo_db = None

# ===================================================================
# --- 3. API ENDPOINTS ---
# ===================================================================

# --- Helper Function (UPDATED WITH DEBUGGING) ---
def get_data_from_postgres(table_name: str):
    if pg_engine is None:
        print(f"Error: get_data_from_postgres called but pg_engine is None.") # DEBUG
        return {"error": "PostgreSQL connection not established."}
    try:
        print(f"Attempting to read table: {table_name}") # DEBUG
        df = pd.read_sql_table(table_name, pg_engine)
        print(f"Successfully read {len(df)} rows from {table_name}") # DEBUG
        return df.to_dict('records')
    except Exception as e:
        print(f"---!!! DATABASE READ ERROR !!!---") # DEBUG
        print(f"Error reading table {table_name}: {e}") # DEBUG
        print(f"---!!! END OF ERROR !!!---") # DEBUG
        return {"error": str(e)}

def get_data_from_mongo(collection_name: str):
    if mongo_db is None:
        return {"error": "MongoDB connection not established."}
    try:
        collection = mongo_db[collection_name]
        data = list(collection.find({}))
        for item in data:
            item['_id'] = str(item['_id'])
        return data
    except Exception as e:
        return {"error": str(e)}

# --- Root Endpoint ---
@app.get("/")
def read_root():
    return {"message": "Welcome to the IoT Sensor API"}

# --- AQ Endpoint ---
@app.get("/api/aq")
def get_aq_data():
    data = get_data_from_postgres('aq_data')
    # data = get_data_from_mongo('aq_data')
    return data

# --- SL Endpoint ---
@app.get("/api/sl")
def get_sl_data():
    data = get_data_from_postgres('sl_data')
    # data = get_data_from_mongo('sl_data')
    return data

# --- WF Endpoint ---
@app.get("/api/wf")
def get_wf_data():
    data = get_data_from_postgres('wf_data')
    # data = get_data_from_mongo('wf_data')
    return data

# This 'if' block is for uvicorn to find the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)