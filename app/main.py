import os
import time
import uuid
from contextlib import contextmanager
from typing import Generator

import psycopg
from fastapi import FastAPI, HTTPException
from prometheus_client import Counter, Histogram, generate_latest
from pydantic import BaseModel, Field
from starlette.responses import Response

APP_NAME = os.getenv("APP_NAME", "airline-booking-api")
DATABASE_URL = os.getenv("DATABASE_URL", "")
APP_MODE = os.getenv("APP_MODE", "normal")

REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency",
    ["method", "path"],
)

app = FastAPI(title="Airline Booking API", version="1.0.0")


class BookingRequest(BaseModel):
    passenger_name: str = Field(min_length=2, max_length=100)
    flight_number: str = Field(pattern=r"^[A-Z]{2,3}-?[0-9]{1,4}$")
    seat: str = Field(pattern=r"^[0-9]{1,2}[A-F]$")


class BookingResponse(BookingRequest):
    booking_id: str
    status: str


@contextmanager
def db_connection() -> Generator[psycopg.Connection, None, None]:
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured")
    conn = psycopg.connect(DATABASE_URL, connect_timeout=5)
    try:
        yield conn
    finally:
        conn.close()


def init_db() -> None:
    if not DATABASE_URL:
        return
    with db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS bookings (
                booking_id UUID PRIMARY KEY,
                passenger_name VARCHAR(100) NOT NULL,
                flight_number VARCHAR(10) NOT NULL,
                seat VARCHAR(4) NOT NULL,
                status VARCHAR(20) NOT NULL,
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        conn.commit()


@app.on_event("startup")
def startup() -> None:
    if APP_MODE == "crash":
        raise RuntimeError("Intentional startup failure for incident drill")
    init_db()


@app.middleware("http")
async def metrics_middleware(request, call_next):
    started = time.perf_counter()
    response = await call_next(request)
    duration = time.perf_counter() - started
    REQUEST_COUNT.labels(request.method, request.url.path, response.status_code).inc()
    REQUEST_LATENCY.labels(request.method, request.url.path).observe(duration)
    return response


@app.get("/health")
def health():
    return {"status": "ok", "service": APP_NAME}


@app.get("/ready")
def ready():
    if not DATABASE_URL:
        return {"status": "ready", "database": "not-configured"}
    try:
        with db_connection() as conn:
            conn.execute("SELECT 1")
        return {"status": "ready", "database": "ok"}
    except Exception as exc:
        raise HTTPException(status_code=503, detail="database unavailable") from exc


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type="text/plain; version=0.0.4")


@app.post("/bookings", response_model=BookingResponse, status_code=201)
def create_booking(request: BookingRequest):
    booking_id = uuid.uuid4()
    if not DATABASE_URL:
        return BookingResponse(**request.model_dump(), booking_id=str(booking_id), status="CONFIRMED")

    try:
        with db_connection() as conn:
            conn.execute(
                """
                INSERT INTO bookings (booking_id, passenger_name, flight_number, seat, status)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (booking_id, request.passenger_name, request.flight_number, request.seat, "CONFIRMED"),
            )
            conn.commit()
        return BookingResponse(**request.model_dump(), booking_id=str(booking_id), status="CONFIRMED")
    except Exception as exc:
        raise HTTPException(status_code=500, detail="booking persistence failed") from exc
