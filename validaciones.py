from datetime import datetime

def validar_fechas(fecha_inicio, fecha_fin):
    inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fin = datetime.strptime(fecha_fin, "%Y-%m-%d")

    dias = (fin - inicio).days

    if dias < 7:
        return False, "Las vacaciones deben ser mínimo de 7 días"

    dia_fin = fin.weekday()

    if dia_fin == 4 or dia_fin == 5:
        return False, "Las vacaciones no pueden terminar viernes o sábado"

    return True, "Fechas válidas"