from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.ofertas import router as ofertas_routes
from routes.agent import router as agent_routes

app = FastAPI(title="JobAgent API", version="0.1.0")

app.add_middleware(CORSMiddleware)

app.include_router(ofertas_routes, prefix="/api/v1")
app.include_router(agent_routes, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "JobAgent API running succesfully"}
