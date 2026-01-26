# SmartPeopleCounter

An intelligent system for real-time people counting, using video detection, tracking, and suspicious entry alerts. The project offers an interactive dashboard, record history, and database integration for continuous monitoring.

## Main Features

Real-time counting of entries, exits, and total people in a room.

Visual alerts for suspicious entries (when exits exceed entries).

Responsive dashboard displaying counters and the history of the last 25 records.

Data persistence using MySQL, ensuring a complete history.

Support for mobile phone cameras via IP Webcam or computer webcam.

## 🛠️ Technologies Used

- Backend: Python, FastAPI, Ultraytics YOLOv8, OpenCV, asyncio, threading
- Frontend: HTML, Bootstrap 5, JavaScript, WebSocket
- Database: MySQL

## System Flow

Video Capture: the mobile camera (IP Webcam) or webcam sends images to the backend.

Video Processing: the YOLOv8 model detects people, and the Centroid Tracker tracks movement.

Counting and Alerts: entries and exits are counted, and alerts are triggered when there is a suspicion.

Frontend Update: data is sent in real-time via WebSocket to the dashboard.

Database Logging: changes in the counters are saved in MySQL for historical records.

## 💻 Environment Setup

### Backend

1. Install dependencies:

    - pip install -r requirements.txt

2. Set up the MySQL database and update database.py with your credentials.

    - Create a database with the table "people_count" with the attributes: id, entered, exited, current_people, timestamp

3. Start the API:

    - uvicorn backend.main:app --reload

### Frontend

1. The frontend is located in the /frontend folder and is built with HTML, Bootstrap, and JavaScript.

2. To open it, simply open the file:

    - frontend/index.html

The page automatically connects to the backend via WebSocket and starts the counter if it is not running.

## API Endpoints
| Method    | Endpoint   | Description                                             |
| --------- | ---------- | ------------------------------------------------------- |
| GET       | `/start`   | Start the people counter (if it's not already active)   |
| GET       | `/history` | Returns the history of the last 25 entries              |
| WebSocket | `/ws`      | Connection to send real-time data to the frontend       |

WebSocket	/ws	Connection to send real-time data to the frontend

## Example of Use

- When opening the index.html page, the count starts automatically.

- Entries, exits, and the total are updated in real time.

- Alerts of suspicious entries flash in red on the screen and on the frontend.

- History of the last 25 records is displayed and updated every 5 seconds.

## Developer
**[Jeremias Dinzinga](https://www.linkedin.com/in/jeremias-dinzinga-a9867b221/)**