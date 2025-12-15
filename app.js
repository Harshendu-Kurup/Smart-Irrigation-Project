console.log("✅ app.js loaded");

const BACKEND_URL = "https://smart-irrigation-project-7oky.onrender.com";

document.addEventListener("DOMContentLoaded", () => {
  updateDateTime();
  loadLatest();
  drawSoilChart();
  drawTempChart();

  setInterval(updateDateTime, 1000);
  setInterval(loadLatest, 15000);
  setInterval(drawSoilChart, 15000);
  setInterval(drawTempChart, 15000);
});

// ================= DATE & TIME =================
function updateDateTime() {
  const now = new Date();
  document.getElementById("date").innerText = now.toLocaleDateString();
  document.getElementById("time").innerText = now.toLocaleTimeString();
}

// ================= LATEST DATA =================
async function loadLatest() {
  try {
    const res = await fetch(`${BACKEND_URL}/latest`);
    const data = await res.json();
    if (!data) return;

    document.getElementById("soil").innerText = data.soil_moisture + " %";
    document.getElementById("temp").innerText = data.temperature + " °C";
    document.getElementById("hum").innerText = data.humidity + " %";
    document.getElementById("light").innerText = data.light;
    document.getElementById("water").innerText = data.water_level + " %";

    // Pump status
    document.getElementById("pump").innerText =
      data.irrigation_event === 1 ? "ON" : "OFF";

    // Decision
    document.getElementById("decision").innerText =
      data.decision_reason || "--";

    document.getElementById("reason").innerText =
      data.decision_reason || "--";

    document.getElementById("lastIrrigated").innerText =
      data.last_irrigated
        ? new Date(data.last_irrigated).toLocaleString()
        : "Never";

    // Weather (only rain prediction exists)
    /*document.getElementById("weatherDesc").innerText =
      data.rain_next_3h > 0 ? "Rain Expected" : "No Rain Expected";

    document.getElementById("apiTemp").innerText =
    data.api_temp !== null ? data.api_temp : "---";

    document.getElementById("apiHum").innerText =
    data.api_humidity !== null ? data.api_humidity  : "---";*/


    // Weather Section

// 1. Update Description (shows "Rain Expected" if rain is predicted, otherwise shows the actual weather like "clouds" or "clear sky")
   document.getElementById("weatherDesc").innerText = 
   data.rain_next_3h > 0 ? "Rain Expected" : (data.weather_desc || "--");

// 2. Update Temperature (Checks if data exists, otherwise shows --)
   document.getElementById("apiTemp").innerText = 
   (data.api_temp !== undefined && data.api_temp !== null) ? data.api_temp : "--";

// 3. Update Humidity
    document.getElementById("apiHum").innerText = 
   (data.api_humidity !== undefined && data.api_humidity !== null) ? data.api_humidity : "--";


  } catch (err) {
    console.error("❌ loadLatest failed", err);
  }
}

// ================= MANUAL CONTROL =================
async function pumpOn() {
  await fetch(`${BACKEND_URL}/manual-control`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pump: 1, minutes: 5 })
  });
  alert("Pump ON command sent");
}

async function pumpOff() {
  await fetch(`${BACKEND_URL}/manual-control`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pump: 0, minutes: 0 })
  });
  alert("Pump OFF command sent");
}

// ================= HISTORY =================
async function fetchHistory() {
  const res = await fetch(`${BACKEND_URL}/history?limit=20`);
  return await res.json();
}

// ================= CHARTS =================
let soilChart, tempChart;

async function drawSoilChart() {
  const history = await fetchHistory();
  const labels = history.map(d =>
    new Date(d.timestamp).toLocaleTimeString()
  ).reverse();

  const soilData = history.map(d => d.soil_moisture).reverse();

  if (soilChart) soilChart.destroy();

  soilChart = new Chart(document.getElementById("soilChart"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Soil Moisture (%)",
        data: soilData,
        borderColor: "green",
        tension: 0.3
      }]
    }
  });
}

async function drawTempChart() {
  const history = await fetchHistory();
  const labels = history.map(d =>
    new Date(d.timestamp).toLocaleTimeString()
  ).reverse();

  const tempData = history.map(d => d.temperature).reverse();

  if (tempChart) tempChart.destroy();

  tempChart = new Chart(document.getElementById("tempChart"), {
    type: "line",
    data: {
      labels,
      datasets: [{
        label: "Temperature (°C)",
        data: tempData,
        borderColor: "orange",
        tension: 0.3
      }]
    }
  });
}
