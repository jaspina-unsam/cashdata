from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from cashdata.infrastructure.api.routers import (
    purchases,
    credit_cards,
    categories,
    users,
    monthly_statements,
)

app = FastAPI(
    title="CashData API",
    version="3.0.0",
    description="API de gestión financiera personal"
)

# CORS para desarrollo (permitir frontend en localhost:5173 y 5174)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(purchases.router)
app.include_router(credit_cards.router)
app.include_router(categories.router)
app.include_router(monthly_statements.router)

@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": "CashData",
        "version": "3.0.0"
    }

@app.get("/")
def root():
    return {
        "message": "CashData API - Backend Running",
        "docs": "/docs"
    }