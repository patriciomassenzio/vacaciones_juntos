import os
import psycopg

def conectar():
    try:
        db_url = os.getenv("DATABASE_URL")

        if not db_url:
            raise Exception("DATABASE_URL no está definida")

        return psycopg.connect(db_url)

    except Exception as e:
        print("❌ ERROR DE CONEXIÓN:")
        print(e)
        raise e