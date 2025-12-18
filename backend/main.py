from fastapi import FastAPI

app = FastAPI(
    title="SmartPeopleCounter",
    description="Sistema inteligente de contagem de pessoas",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "SmartPeopleCounter API está online"}
