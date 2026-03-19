from database import conectar
from auth import hash_password, verificar_password

def crear_usuario(dni, nombres, cargo, email, password, rol="usuario"):
    conn = conectar()
    cursor = conn.cursor()

    password_hash = hash_password(password)

    query = """
    INSERT INTO usuarios (dni, nombres, cargo, email, password_hash, rol)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id
    """

    cursor.execute(query, (dni, nombres, cargo, email, password_hash, rol))
    usuario_id = cursor.fetchone()[0]
    conn.commit()

    cursor.close()
    conn.close()

    return usuario_id

def obtener_usuario_por_dni(dni):
    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT id, dni, nombres, cargo, email, password_hash, rol
    FROM usuarios
    WHERE dni = %s
    """

    cursor.execute(query, (dni,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return None

    return {
        "id": row[0],
        "dni": row[1],
        "nombres": row[2],
        "cargo": row[3],
        "email": row[4],
        "password_hash": row[5],
        "rol": row[6]
    }

def login_usuario(dni, password):
    usuario = obtener_usuario_por_dni(dni)

    if not usuario:
        return None

    if not verificar_password(password, usuario["password_hash"]):
        return None

    return {
        "id": usuario["id"],
        "dni": usuario["dni"],
        "nombres": usuario["nombres"],
        "cargo": usuario["cargo"],
        "email": usuario["email"],
        "rol": usuario["rol"]
    }