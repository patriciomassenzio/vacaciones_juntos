from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    password = str(password).strip()

    # 🔥 seguridad extra
    if len(password.encode("utf-8")) > 72:
        password = password[:72]

    return pwd_context.hash(password)

def verificar_password(password: str, password_hash: str) -> bool:
    password = str(password).strip()
    password_hash = str(password_hash).strip()

    if len(password.encode("utf-8")) > 72:
        password = password[:72]

    return pwd_context.verify(password, password_hash)