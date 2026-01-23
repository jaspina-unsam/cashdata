from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.infrastructure.api.routers import (
    purchases,
    credit_cards,
    categories,
    users,
    monthly_statements,
    installments,
    payment_methods,
    cash_accounts,
    bank_accounts,
    digital_wallets,
    budgets,
    exchange_rates,
)

app = FastAPI(
    title="CashData API",
    version="3.0.0",
    description="API de gestión financiera personal",
)

# CORS para desarrollo (permitir frontend en localhost:5173 y 5174)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://192.168.0.131",
        "http://cumulonimbus.local",
    ],
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
app.include_router(installments.router)
app.include_router(payment_methods.router)
app.include_router(cash_accounts.router)
app.include_router(bank_accounts.router)
app.include_router(digital_wallets.router)
app.include_router(budgets.router)
app.include_router(exchange_rates.router)


@app.get("/health")
def health():
    return {"status": "ok", "app": "CashData", "version": "0.2.0"}


@app.get("/")
def root():
    return {"message": "CashData API - Backend Running", "docs": "/docs"}
