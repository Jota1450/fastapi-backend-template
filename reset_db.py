#!/usr/bin/env python3
"""
Script para reiniciar la base de datos
Ejecuta: python reset_db.py
"""

from sqlalchemy import text
from sqlmodel import create_engine

from app.config.config import settings

def reset_database():
    """Elimina todas las tablas y schemas, luego aplica las migraciones"""
    engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))
    
    print("🔄 Reiniciando base de datos...")
    
    with engine.connect() as connection:
        # Eliminar todas las tablas en el schema users
        print("  - Eliminando schema 'users' y todas sus tablas...")
        connection.execute(text("DROP SCHEMA IF EXISTS users CASCADE"))
        
        # Eliminar tabla de versiones de Alembic
        print("  - Eliminando historial de migraciones de Alembic...")
        connection.execute(text("DROP TABLE IF EXISTS alembic_version CASCADE"))
        
        # Confirmar cambios
        connection.commit()
    
    print("✅ Base de datos reiniciada correctamente")
    print("\n📝 Próximos pasos:")
    print("   1. Ejecuta: alembic upgrade head")
    print("   2. (Opcional) Ejecuta: python -m app.utils.initial_data para crear datos iniciales")

if __name__ == "__main__":
    reset_database()

