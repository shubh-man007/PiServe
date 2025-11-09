# PiServe

PiServe is an IoT server application designed for the Raspberry Pi that enables real-time video streaming with integrated object detection and collects environmental data from IoT sensors such as the ESP32 with a DHT11 sensor.  
It integrates **InfluxDB** for time-series data storage and **Grafana** for observability and visualization.

---

## Features

- Real-time temperature and humidity monitoring using DHT11 sensors connected to ESP32 devices  
- RESTful API endpoints for data exchange  
- InfluxDB for time-series data persistence  
- Grafana dashboards for live analytics and alerts  
- Real-time object detection using pre-trained models  
- Live camera streaming via HTTP endpoint  

---

## Project Structure

```
PiServe/
├── server_peripherals/          # Python backend application
│   ├── main.py                  # FastAPI server implementation
│   ├── *.caffemodel             # Pre-trained object detection models
│   └── *.prototxt               # Model configuration files
├── venv/                        # Python virtual environment
└── requirements.txt             # Python dependencies

```

--- 

## System Architecture


---

## Installation

### 1. Clone Repository

```bash
git clone https://github.com/shubh-man007/PiServe.git
cd PiServe
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Start Backend Server

```bash
cd server_peripherals
uvicorn main:app --reload --host 0.0.0.0 --port 8000
http://<raspberry-pi-ip>:8086 # Influx DB
http://<raspberry-pi-ip>:3000 #Grafana
```

---

## Usage

### Accessing Camera Feed

Open in a web browser:

```
http://<raspberry-pi-ip>:8000/video-feed/
```

### ESP32 Sensor Integration

1. Configure your ESP32 with the Raspberry Pi’s IP in its Wi-Fi client code.
2. Ensure both ESP32 and Raspberry Pi are on the same network.
3. The ESP32 automatically sends temperature and humidity readings via `POST /sensor-data/`.

---

## API Endpoints

| Endpoint        | Method | Description                                             |
| --------------- | ------ | ------------------------------------------------------- |
| `/sensor-data/` | POST   | Receives sensor data from ESP32 and writes to InfluxDB  |
| `/sensor-data/` | GET    | Fetches sensor data from InfluxDB                       |
| `/video-feed/`  | GET    | Streams the processed video feed with detection overlay |

---