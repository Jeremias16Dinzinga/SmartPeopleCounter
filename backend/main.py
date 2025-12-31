from fastapi import FastAPI, Depends

app = FastAPI()

from people_counter import start_people_counter

@app.get("/start-counter")
def start_counter():
    stream_url = "http://192.168.1.10:8080/video"   
    start_people_counter(stream_url)
    return {"status": "Contador iniciado"}
