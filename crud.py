from database import conectar
from datetime import datetime

# =========================
# SOLICITUDES
# =========================

def guardar_solicitud(usuario_id, dni, periodo_vacacional, fecha_inicio, fecha_fin):
    try:
        print("💾 Guardando en DB...")

        conn = conectar()
        cursor = conn.cursor()

        inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

        total_dias = (fin - inicio).days

        query = """
        INSERT INTO solicitudes
        (usuario_id, dni, periodo_vacacional, tipo_solicitud, fecha_inicio, fecha_fin, total_dias, estado)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
        """

        cursor.execute(
            query,
            (usuario_id, dni, periodo_vacacional, "vacaciones", fecha_inicio, fecha_fin, total_dias, "pendiente")
        )

        id_solicitud = cursor.fetchone()[0]
        conn.commit()

        cursor.close()
        conn.close()

        print("✅ Guardado correctamente, ID:", id_solicitud)
        return id_solicitud

    except Exception as e:
        print("❌ ERROR GUARDANDO:")
        print(e)
        raise e


def actualizar_documento(id_solicitud, nombre_documento):
    try:
        conn = conectar()
        cursor = conn.cursor()

        query = """
        UPDATE solicitudes
        SET documento = %s
        WHERE id = %s
        """

        cursor.execute(query, (nombre_documento, id_solicitud))
        conn.commit()

        cursor.close()
        conn.close()

        print("✅ Documento actualizado en DB")

    except Exception as e:
        print("❌ ERROR ACTUALIZANDO DOCUMENTO:")
        print(e)
        raise e


def obtener_solicitudes_usuario(usuario_id, limite=10):
    try:
        conn = conectar()
        cursor = conn.cursor()

        query = """
        SELECT id, dni, periodo_vacacional, fecha_inicio, fecha_fin, total_dias, estado, fecha_creacion, documento
        FROM solicitudes
        WHERE usuario_id = %s
        ORDER BY fecha_creacion DESC
        LIMIT %s
        """

        cursor.execute(query, (usuario_id, limite))
        rows = cursor.fetchall()

        cursor.close()
        conn.close()

        solicitudes = []
        for row in rows:
            solicitudes.append({
                "id": row[0],
                "dni": row[1],
                "periodo_vacacional": row[2],
                "fecha_inicio": str(row[3]),
                "fecha_fin": str(row[4]),
                "dias": row[5],
                "estado": row[6],
                "fecha_creacion": str(row[7]),
                "documento": row[8]
            })

        return solicitudes

    except Exception as e:
        print("❌ ERROR OBTENIENDO SOLICITUDES USUARIO:")
        print(e)
        raise e


# =========================
# SESIONES DE CHAT
# =========================

def obtener_sesion(usuario_id):
    try:
        conn = conectar()
        cursor = conn.cursor()

        query = """
        SELECT usuario_id, estado, fecha_inicio_temp, fecha_fin_temp, duracion_temp, ultimo_mensaje
        FROM chat_sesiones
        WHERE usuario_id = %s
        """

        cursor.execute(query, (usuario_id,))
        row = cursor.fetchone()

        cursor.close()
        conn.close()

        if not row:
            return None

        return {
            "usuario_id": row[0],
            "estado": row[1],
            "fecha_inicio_temp": str(row[2]) if row[2] else None,
            "fecha_fin_temp": str(row[3]) if row[3] else None,
            "duracion_temp": row[4],
            "ultimo_mensaje": row[5]
        }

    except Exception as e:
        print("❌ ERROR OBTENIENDO SESIÓN:")
        print(e)
        raise e


def guardar_o_actualizar_sesion(usuario_id, estado, fecha_inicio_temp=None, fecha_fin_temp=None, duracion_temp=None, ultimo_mensaje=None):
    try:
        conn = conectar()
        cursor = conn.cursor()

        query = """
        INSERT INTO chat_sesiones (usuario_id, estado, fecha_inicio_temp, fecha_fin_temp, duracion_temp, ultimo_mensaje, actualizado_en)
        VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (usuario_id)
        DO UPDATE SET
            estado = EXCLUDED.estado,
            fecha_inicio_temp = EXCLUDED.fecha_inicio_temp,
            fecha_fin_temp = EXCLUDED.fecha_fin_temp,
            duracion_temp = EXCLUDED.duracion_temp,
            ultimo_mensaje = EXCLUDED.ultimo_mensaje,
            actualizado_en = CURRENT_TIMESTAMP
        """

        cursor.execute(
            query,
            (usuario_id, estado, fecha_inicio_temp, fecha_fin_temp, duracion_temp, ultimo_mensaje)
        )

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Sesión guardada/actualizada")

    except Exception as e:
        print("❌ ERROR GUARDANDO SESIÓN:")
        print(e)
        raise e


def limpiar_sesion(usuario_id):
    try:
        conn = conectar()
        cursor = conn.cursor()

        query = "DELETE FROM chat_sesiones WHERE usuario_id = %s"
        cursor.execute(query, (usuario_id,))

        conn.commit()
        cursor.close()
        conn.close()

        print("✅ Sesión limpiada")

    except Exception as e:
        print("❌ ERROR LIMPIANDO SESIÓN:")
        print(e)
        raise e