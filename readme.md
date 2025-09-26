# PiServe

PiServe is an IoT server application designed for Raspberry Pi that provides real-time camera streaming with integrated object detection capabilities and receives sensor data from connected IoT devices such as ESP32 with DHT11 sensors.

## Features

- Live camera feed streaming
- Real-time object detection using pre-trained models
- DHT11 sensor data collection from ESP32 devices
- RESTful API endpoints
- Optional React-based dashboard interface

## Project Structure

```
PiServe/
├── server_peripherals/          # Python backend application
│   ├── main.py                  # FastAPI server implementation
│   ├── *.caffemodel            # Pre-trained object detection models
│   └── *.prototxt              # Model configuration files
├── iot-dashboard/              # React frontend application (optional)
├── venv/                       # Python virtual environment
└── requirements.txt            # Python dependencies
```

## Prerequisites

- Raspberry Pi with camera module
- Python 3.7 or higher
- ESP32 with DHT11 sensor (for sensor data features)
- Node.js and npm (for optional dashboard)

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
```

## Usage

### Accessing Camera Feed

Navigate to the following URL in your web browser:
```
http://<raspberry-pi-ip>:8000/video-feed/
```

### ESP32 Sensor Integration

1. Configure your ESP32 code with the Raspberry Pi's IP address
2. Ensure both devices are connected to the same network
3. The ESP32 will automatically transmit DHT11 sensor readings every 5 seconds

### Optional Dashboard Setup

For the React-based dashboard interface:

```bash
cd iot-dashboard
npm install
npm start
```

Access the dashboard at: `http://localhost:3000`

## API Endpoints

The server provides RESTful API endpoints for:
- Video streaming
- Sensor data retrieval (GET and POST)

