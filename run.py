#!/usr/bin/env python3
"""
Script de inicio para la aplicación FastAPI
Ejecuta: python run.py
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info"
    )
