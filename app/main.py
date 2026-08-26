from fastapi import FastAPI

app = FastAPI(title="Discharge Summary Generator")

@app.get("/health")
def health():
    return {"status": "ok"}