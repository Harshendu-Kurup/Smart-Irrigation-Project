from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import os
import numpy as np
import requests
import pymongo
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

# ================= CONFIG =================
API_KEY = "ddddec6f094f8cbdc75eb7f15445c786"
LAT = 9.456717872532293
LON = 76.52561688145256

DRY_THRESHOLD = 15
TANK_LOW_THRESHOLD = 15

MONGO_URI = "mongodb+srv://Harshendu:Harshendu123@smartirrigationcluster.bun2uzw.mongodb.net/"
client = pymongo.MongoClient(MONGO_URI)
db = client["SmartIrrigation"]
collection = db["sensor_logs"]

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "irrigation_best_model.pkl")
model = joblib.load(MODEL_PATH)

app = FastAPI(title="Smart Irrigation Backend")

# ================= CORS =================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ================= WEATHER =================
def get_weather():
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={LAT}&lon={LON}&appid={API_KEY}&units=metric"
    data = requests.get(url).json()
    rain_3h = data["list"][0].get("rain", {}).get("3h", 0.0)
    return rain_3h

# ================= ESP INPUT =================
class SensorData(BaseModel):
    soil_moisture: float
    temperature: float
    humidity: float
    light: float
    water_level: float

# ================= ROUTES =================
@app.get("/")
def root():
    return {"status": "Smart Irrigation Backend Running"}

@app.get("/latest")
def get_latest_data():
    latest = collection.find_one(sort=[("timestamp", -1)])
    if latest:
        latest["_id"] = str(latest["_id"])
    return latest

@app.get("/history")
def get_history(limit: int = 50):
    data = list(collection.find().sort("timestamp", -1).limit(limit))
    for d in data:
        d["_id"] = str(d["_id"])
    return data

manual_command = {"pump": 0, "minutes": 0}

@app.post("/manual-control")
def manual_control(command: dict):
    manual_command["pump"] = command.get("pump", 0)
    manual_command["minutes"] = command.get("minutes", 0)
    return {"status": "Command saved", "command": manual_command}

# ================= CORE LOGIC =================
@app.post("/sensor-data")
def receive_sensor_data(sensor: SensorData):

    now = datetime.now()

    # ---------- ML prediction ----------
    X = np.array([[sensor.soil_moisture,
                   sensor.temperature,
                   sensor.humidity,
                   sensor.light]])
    irrigation_needed = int(model.predict(X)[0])

    # ---------- Weather ----------
    rain_next_3h = get_weather()

    # ---------- Previous DB entry ----------
    last_entry = collection.find_one(sort=[("timestamp", -1)])
    last_irrigation = collection.find_one(
        {"irrigation_event": 1},
        sort=[("timestamp", -1)]
    )

    # ---------- Time since irrigation ----------
    if last_irrigation:
        last_irrigated_time = last_irrigation["timestamp"]
        time_since_irrigation = (now - last_irrigated_time).total_seconds() / 60
    else:
        last_irrigated_time = None
        time_since_irrigation = None

    # ---------- Minutes gap ----------
    minutes_gap = (
        (now - last_entry["timestamp"]).total_seconds() / 60
        if last_entry else 0
    )

    # ---------- Moisture drop rate ----------
    moisture_drop_rate = (
        (sensor.soil_moisture - last_entry["soil_moisture"]) / minutes_gap
        if last_entry and minutes_gap > 0 else 0.0
    )

    # ---------- Decision Logic ----------
    pump = 0
    irrigation_event = 0
    alert = None
    reason = "No irrigation required"

    # 🚨 Tank safety
    if sensor.water_level < TANK_LOW_THRESHOLD:
        pump = 0
        irrigation_event = 0
        alert = "Water tank empty or critically low"
        reason = "Irrigation blocked to protect pump"

    else:
        if irrigation_needed == 1:
            if rain_next_3h < 2.0:
                pump = 1
                irrigation_event = 1
                reason = "Soil dry and no rain expected"
            else:
                reason = "Rain expected, irrigation delayed"

    if irrigation_event == 1:
        last_irrigated_time = now
        time_since_irrigation = 0

    # ---------- Final DB record ----------
    record = {
        "timestamp": now,
        "soil_moisture": sensor.soil_moisture,
        "temperature": sensor.temperature,
        "humidity": sensor.humidity,
        "light": sensor.light,
        "water_level": sensor.water_level,

        "irrigation_needed": irrigation_needed,
        "irrigation_event": irrigation_event,
        "last_irrigated": last_irrigated_time,
        "time_since_irrigation": time_since_irrigation,
        "minutes": round(minutes_gap, 2),
        "moisture_drop_rate": round(moisture_drop_rate, 4),

        "rain_next_3h": rain_next_3h,
        "decision_reason": reason,
        "tank_alert": alert
    }

    collection.insert_one(record)

    return {
        "pump": pump,
        "minutes": 5 if pump == 1 else 0,
        "reason": reason,
        "alert": alert
    }
