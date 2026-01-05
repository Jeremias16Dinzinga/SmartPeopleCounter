from fastapi import FastAPI, Depends
from people_counter import start_people_counter

app = FastAPI(title="SmartPeopleCounter")

@app.get("/start-counter")
def start_counter():
    stream_url = "http://192.168.1.10:8080/video"   
    start_people_counter(stream_url)
    return {"status": "Contador iniciado"}
