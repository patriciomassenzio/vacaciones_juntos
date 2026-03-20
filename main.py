from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import traceback
import os
from datetime import datetime

from generador_documentos import generar_solicitud
from crud import (
    guardar_solicitud,
    actualizar_documento,
    obtener_solicitudes_usuario
)
from crud_usuarios import crear_usuario, login_usuario
from crud_saldos import validar_saldo_en_db, obtener_saldos_por_dni
from validaciones import validar_fechas

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELOS
# =========================

class RegistroUsuario(BaseModel):
    dni: str
    nombres: str
    cargo: str | None = None
    email: str | None = None
    password: str

class LoginData(BaseModel):
    dni: str
    password: str

class ValidarSolicitud(BaseModel):
    dni: str
    fecha_inicio: str
    fecha_fin: str

class CrearSolicitud(BaseModel):
    usuario_id: int
    dni: str
    fecha_inicio: str
    fecha_fin: str
    periodo_vacacional: str

class EstadoUpdate(BaseModel):
    id: int
    estado: str

# =========================
# ENDPOINTS BÁSICOS
# =========================

@app.get("/")
def home():
    return {"mensaje": "API de vacaciones funcionando"}

@app.post("/registro")
def registro(data: RegistroUsuario):
    try:
        usuario_id = crear_usuario(
            dni=data.dni,
            nombres=data.nombres,
            cargo=data.cargo,
            email=data.email,
            password=data.password
        )
        return {"mensaje": "Usuario creado correctamente", "usuario_id": usuario_id}
    except Exception as e:
        return {"error": str(e)}

@app.post("/login")
def login(data: LoginData):
    try:
        usuario = login_usuario(data.dni, data.password)

        if not usuario:
            return {"error": "Credenciales inválidas"}

        return {
            "mensaje": "Login correcto",
            "usuario": usuario
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/saldo/{dni}")
def ver_saldo(dni: str):
    try:
        saldos = obtener_saldos_por_dni(dni)
        return {"saldos": saldos}
    except Exception as e:
        return {"error": str(e)}

# =========================
# 🔥 NUEVO: VALIDAR SOLICITUD
# =========================

@app.post("/validar-solicitud")
def validar_solicitud(data: ValidarSolicitud):
    try:
        fecha_inicio = data.fecha_inicio
        fecha_fin = data.fecha_fin

        # 1. validar fechas
        valido, mensaje = validar_fechas(fecha_inicio, fecha_fin)

        if not valido:
            return {
                "ok": False,
                "mensaje": mensaje
            }

        # 2. calcular días
        inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
        dias = (fin_dt - inicio_dt).days + 1

        # 3. validar saldo
        saldo_ok, mensaje_saldo, periodo = validar_saldo_en_db(
            dni=data.dni,
            dias_solicitados=dias,
            periodo_mencionado=None
        )

        if not saldo_ok:
            return {
                "ok": False,
                "mensaje": mensaje_saldo
            }

        return {
            "ok": True,
            "mensaje": mensaje_saldo,
            "periodo_vacacional": periodo,
            "dias": dias
        }

    except Exception as e:
        print(traceback.format_exc())
        return {"error": str(e)}

# =========================
# 🔥 NUEVO: CREAR SOLICITUD
# =========================

@app.post("/crear-solicitud")
def crear_solicitud(data: CrearSolicitud):
    try:
        id_solicitud = guardar_solicitud(
            data.usuario_id,
            data.dni,
            data.periodo_vacacional,
            data.fecha_inicio,
            data.fecha_fin
        )

        nombre_documento = generar_solicitud(
            f"Usuario {data.usuario_id}",
            data.fecha_inicio,
            data.fecha_fin,
            id_solicitud
        )

        actualizar_documento(id_solicitud, nombre_documento)

        return {
            "ok": True,
            "mensaje": "Solicitud registrada correctamente",
            "id_solicitud": id_solicitud,
            "documento": nombre_documento
        }

    except Exception as e:
        print(traceback.format_exc())
        return {"error": str(e)}

# =========================
# HISTORIAL
# =========================

@app.get("/mis-solicitudes/{usuario_id}")
def mis_solicitudes(usuario_id: int):
    try:
        solicitudes = obtener_solicitudes_usuario(usuario_id, limite=20)
        return {"solicitudes": solicitudes}
    except Exception as e:
        return {"error": str(e)}

# =========================
# ADMIN
# =========================

@app.put("/solicitud/estado")
def cambiar_estado(data: EstadoUpdate):
    from database import conectar
    try:
        conn = conectar()
        cursor = conn.cursor()

        query = """
        UPDATE solicitudes
        SET estado = %s
        WHERE id = %s
        """

        cursor.execute(query, (data.estado, data.id))
        conn.commit()

        cursor.close()
        conn.close()

        return {"mensaje": "Estado actualizado correctamente"}
    except Exception as e:
        return {"error": str(e)}

# =========================
# DOCUMENTOS
# =========================

@app.get("/documento/{nombre_archivo}")
def descargar_documento(nombre_archivo: str):
    try:
        ruta = os.path.join("documentos", nombre_archivo)

        if not os.path.exists(ruta):
            return {"error": "Archivo no encontrado"}

        return FileResponse(
            path=ruta,
            filename=nombre_archivo,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    except Exception as e:
        return {"error": str(e)}