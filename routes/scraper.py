from fastapi import HTTPException, APIRouter, Depends, status
from sqlalchemy.orm import Session
from database import SessionLocal
from repositories import oferta_repository

router = APIRouter(prefix="/scraper", tags=["Scraper"])

@router.post("/linkedin", status_code=status.HTTP_200_OK)

@router.post("/infojobs", status_code=status.HTTP_200_OK)

@router.post("/indeed", status_code=status.HTTP_200_OK)

@router.post("/glassdoor", status_code=status.HTTP_200_OK)