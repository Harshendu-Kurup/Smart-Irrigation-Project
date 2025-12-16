# Smart-Irrigation-Project
🌱 Smart Irrigation System (AI + IoT + Cloud)

An AI-powered Smart Irrigation System that integrates ESP32-based sensor data, machine learning, weather forecasting, cloud backend, and a live web dashboard to optimize irrigation decisions and reduce water wastage.

This project was developed as part of an academic technical project and demonstrated with a working hardware prototype and cloud-connected dashboard.


---

📌 Key Features

🌱 Real-time soil moisture monitoring

🌡 Temperature & humidity sensing

☀ Light intensity measurement

💧 Water tank level monitoring

🌦 Live weather & rain prediction (OpenWeatherMap API)

🤖 ML-based irrigation decision logic

🚿 Automatic + manual pump control

📊 Live dashboard with graphs & trends

☁ Cloud deployment using Render

🗄 MongoDB for historical data storage



---

📂 Repository Structure

Smart-Irrigation-Project/
│
├── app.py                  # FastAPI backend (main server)
├── main.py                 # Alternate backend entry (not used in final demo)
├── requirements.txt        # Python dependencies
├── runtime.txt             # Python runtime version for Render
├── irrigation_best_model.pkl  # Trained ML model
│
├── esp_backend.ino         # ESP32 firmware
│
├── index.html              # Dashboard UI
├── styles.css              # Dashboard styling
├── app.js                  # Dashboard logic (API + charts)
│
├── README.md               # Project documentation
└── __pycache__/            # Python cache (can be ignored)


---

🧠 System Architecture (High Level)

ESP32 Sensors
   ↓
FastAPI Backend (Render)
   ↓
ML Model + Weather API
   ↓
MongoDB Atlas
   ↓
Web Dashboard (HTML/CSS/JS)


---

🧩 Hardware Components Used

Component	Purpose

ESP32	Microcontroller + WiFi
Soil Moisture Sensor	Detect soil dryness
DHT22	Temperature & humidity
LDR	Light intensity
Water Level Sensor	Tank monitoring
Relay Module	Pump control
DC Water Pump	Irrigation
External Power Supply	Pump safety



---

⚙️ Complete Setup & Deployment Guide

🔹 1. Clone the Repository

git clone https://github.com/Harshendu-Kurup/Smart-Irrigation-Project.git
cd Smart-Irrigation-Project


---

🔹 2. Backend Setup (FastAPI + ML)

Step 2.1: Install Python Dependencies

pip install -r requirements.txt


---

Step 2.2: Configure Backend (app.py)

Edit the following inside app.py:

API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"
LAT = <your_latitude>
LON = <your_longitude>

MONGO_URI = "YOUR_MONGODB_ATLAS_URI"


---

Step 2.3: Run Backend Locally (Optional)

python app.py

Or using Uvicorn:

uvicorn app:app --host 0.0.0.0 --port 8000

Test URLs:

http://localhost:8000

http://localhost:8000/latest

http://localhost:8000/history



---

🔹 3. Deploy Backend to Render (Cloud)

1. Push code to GitHub


2. Go to https://render.com


3. Create New → Web Service


4. Select this repository


5. Configure:



Setting	Value

Runtime	Python
Build Command	pip install -r requirements.txt
Start Command	uvicorn app:app --host 0.0.0.0 --port 10000


6. Add environment variables:



API_KEY
MONGO_URI

After deployment, you’ll get a URL like:

https://smart-irrigation-project-7oky.onrender.com


---

🔹 4. ESP32 Firmware Setup

1. Open esp_backend.ino in Arduino IDE


2. Install required libraries:

WiFi

HTTPClient

ArduinoJson

DHT Sensor Library



3. Update credentials:



const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";

String backendURL = "https://your-render-url/sensor-data";

4. Select ESP32 Dev Module


5. Upload code


6. Open Serial Monitor (115200 baud)




---

🔹 5. Frontend Dashboard Setup

Step 5.1: Update Backend URL

Edit app.js:

const BACKEND_URL = "https://your-render-url";


---

Step 5.2: Run Dashboard

Simply open index.html using:

VS Code Live Server
OR

Double click (local demo)



---

📊 Dashboard Features

Live sensor cards

Irrigation decision & reason

Last irrigated time

Weather status

Soil & temperature graphs

Manual pump ON/OFF control



---

🧪 Validation & Results

Sensor data verified via Serial Monitor

Backend verified via /latest & /history

ML predictions matched soil conditions

Weather-based irrigation blocking validated

Dashboard synced with real-time data

Manual override tested successfully



---

🚀 Future Enhancements

Mobile app version

Crop-specific irrigation logic

SMS/Push alerts

Solar-powered system

Multi-field support

