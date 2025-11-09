# from fastapi import FastAPI, Request
# from fastapi.responses import JSONResponse, StreamingResponse
# from influxdb_client import InfluxDBClient, Point, WritePrecision
# from influxdb_client.client.write_api import SYNCHRONOUS
# import cv2
# import numpy as np
# import threading
# import time
# import os
# from dotenv import load_dotenv

# load_dotenv()

# BUCKET = os.getenv("INFLUXDB_BUCKET")
# ORG = os.getenv("INFLUXDB_ORG")
# TOKEN = os.getenv("INFLUXDB_TOKEN")
# URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")

# client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
# write_api = client.write_api(write_options=SYNCHRONOUS)

# app = FastAPI(title="PiServe")

# sensor_data = {"temperature": None, "humidity": None}

# camera_lock = threading.Lock()
# cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
# if not cap.isOpened():
#     print("Cannot open camera")
#     cap.release()
#     cap = None

# # Load detection model
# net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt", "MobileNetSSD_deploy.caffemodel")
# CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
#            "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
#            "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
#            "sofa", "train", "tvmonitor"]
# conf_threshold = 0.5

# def generate_video_feed():
#     global cap
#     while True:
#         if cap is None:
#             break

#         with camera_lock:
#             ret, frame = cap.read()
#             if not ret:
#                 time.sleep(0.1)
#                 continue

#             (h, w) = frame.shape[:2]
#             blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
#                                          0.007843, (300, 300), 127.5)
#             net.setInput(blob)
#             detections = net.forward()

#             for i in range(detections.shape[2]):
#                 confidence = detections[0, 0, i, 2]
#                 if confidence > conf_threshold:
#                     idx = int(detections[0, 0, i, 1])
#                     box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
#                     (startX, startY, endX, endY) = box.astype("int")

#                     label = f"{CLASSES[idx]}: {confidence*100:.2f}%"
#                     cv2.rectangle(frame, (startX, startY), (endX, endY),
#                                   (255, 0, 0), 2)
#                     cv2.putText(frame, label, (startX, startY - 10),
#                                 cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

#             ret, jpeg = cv2.imencode('.jpg', frame)
#             if not ret:
#                 continue
#             frame_bytes = jpeg.tobytes()

#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


# @app.get("/video-feed/")
# def video_feed():
#     if cap is None:
#         return JSONResponse({"error": "Camera not available"}, status_code=500)
#     return StreamingResponse(generate_video_feed(),
#                              media_type="multipart/x-mixed-replace; boundary=frame")


# @app.post("/sensor-data/")
# async def receive_sensor_data(request: Request):
#     try:
#         data = await request.json()
#         temperature = data.get("temperature")
#         humidity = data.get("humidity")

#         if temperature is None or humidity is None:
#             return JSONResponse({"status": "error", "message": "Missing temperature or humidity"}, status_code=400)

#         sensor_data["temperature"] = temperature
#         sensor_data["humidity"] = humidity

#         point = (
#             Point("temperature_humidity")
#             .field("temperature", float(temperature))
#             .field("humidity", float(humidity))
#             .time(time.time_ns(), WritePrecision.NS)
#         )
#         write_api.write(bucket=BUCKET, org=ORG, record=point)

#         return {"status": "success", "temperature": temperature, "humidity": humidity}

#     except Exception as e:
#         return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


# @app.get("/sensor-data/")
# def get_sensor_data():
#     return sensor_data


# @app.on_event("shutdown")
# def shutdown_event():
#     global cap
#     if cap:
#         cap.release()
#         print("Camera released")



from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import cv2
import numpy as np
import threading
import time
import os
from dotenv import load_dotenv

load_dotenv()

BUCKET = os.getenv("INFLUXDB_BUCKET")
ORG = os.getenv("INFLUXDB_ORG")
TOKEN = os.getenv("INFLUXDB_TOKEN")
URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")

# Add this to .env later (localhost -> testing)
WHITELISTED_IPS = [
    "127.0.0.1",           # localhost 
    "::1",                 # IPv6 localhost
    "",        
]

client = InfluxDBClient(url=URL, token=TOKEN, org=ORG)
write_api = client.write_api(write_options=SYNCHRONOUS)

app = FastAPI(title="PiServe")

sensor_data = {"temperature": None, "humidity": None}

camera_lock = threading.Lock()
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
if not cap.isOpened():
    print("Cannot open camera")
    cap.release()
    cap = None

# Load detection model
net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt", "MobileNetSSD_deploy.caffemodel")
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
           "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]
conf_threshold = 0.5


@app.middleware("http")
async def validate_ip(request: Request, call_next):
    client_ip = request.client.host if request.client else None
    
    if request.url.path == "/sensor-data/" and request.method == "POST":
        if client_ip not in WHITELISTED_IPS:
            print(f"[SECURITY] Blocked request from unauthorized IP: {client_ip}")
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={
                    "error": "Access denied",
                    "message": f"IP address {client_ip} is not authorized to send sensor data"
                }
            )
        else:
            print(f"[INFO] Accepted request from whitelisted IP: {client_ip}")
    
    response = await call_next(request)
    return response


def generate_video_feed():
    global cap
    while True:
        if cap is None:
            break

        with camera_lock:
            ret, frame = cap.read()
            if not ret:
                time.sleep(0.1)
                continue

            (h, w) = frame.shape[:2]
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                                         0.007843, (300, 300), 127.5)
            net.setInput(blob)
            detections = net.forward()

            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > conf_threshold:
                    idx = int(detections[0, 0, i, 1])
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    label = f"{CLASSES[idx]}: {confidence*100:.2f}%"
                    cv2.rectangle(frame, (startX, startY), (endX, endY),
                                  (255, 0, 0), 2)
                    cv2.putText(frame, label, (startX, startY - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

            ret, jpeg = cv2.imencode('.jpg', frame)
            if not ret:
                continue
            frame_bytes = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


@app.get("/video-feed/")
def video_feed():
    if cap is None:
        return JSONResponse({"error": "Camera not available"}, status_code=500)
    return StreamingResponse(generate_video_feed(),
                             media_type="multipart/x-mixed-replace; boundary=frame")


@app.post("/sensor-data/")
async def receive_sensor_data(request: Request):
    try:
        data = await request.json()
        temperature = data.get("temperature")
        humidity = data.get("humidity")

        if temperature is None or humidity is None:
            return JSONResponse(
                {"status": "error", "message": "Missing temperature or humidity"},
                status_code=400
            )

        sensor_data["temperature"] = temperature
        sensor_data["humidity"] = humidity

        point = (
            Point("temperature_humidity")
            .field("temperature", float(temperature))
            .field("humidity", float(humidity))
            .time(time.time_ns(), WritePrecision.NS)
        )
        write_api.write(bucket=BUCKET, org=ORG, record=point)

        return {"status": "success", "temperature": temperature, "humidity": humidity}

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=400)


@app.get("/sensor-data/")
def get_sensor_data():
    return sensor_data


@app.get("/")
def root():
    return {
        "status": "online",
        "endpoints": {
            "sensor_data_post": "/sensor-data/ (POST - protected)",
            "sensor_data_get": "/sensor-data/ (GET - public)",
            "video_feed": "/video-feed/ (GET - public)"
        }
    }


@app.on_event("shutdown")
def shutdown_event():
    global cap
    if cap:
        cap.release()
        print("Camera released")