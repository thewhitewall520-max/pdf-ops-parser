"""API entry point with route registration."""

from __future__ import annotations

import uvicorn
from fastapi import FastAPI

from apps.api.routes import routers

app = FastAPI(
    title="PDF Ops Parser API",
    description="Convert invoices and shipping PDFs into structured data",
    version="0.1.0",
)

# Register routes
for router in routers:
    app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "version": "0.1.0"}


def main():
    uvicorn.run(
        "apps.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()
