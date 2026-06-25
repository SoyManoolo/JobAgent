from fastapi import FastAPI, APIRouter

router = APIRouter()

@router.get("/dashboard/ofertas")

@router.get("/dashboard/ofertas/{id}")

@router.get("/dashboard/stats")

@router.delete("/dashboard/ofertas/{id}")

@router.post("/dashboard/ofertas/{id}/aplicar")

@router.patch("/dashboard/ofertas/{id}/notas")
