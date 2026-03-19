import os
import psycopg

def conectar():
    try:
        conexion = psycopg.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", "5432"),
        )
        return conexion
    except Exception as e:
        print("❌ ERROR DE CONEXIÓN:")
        print(e)
        raise e