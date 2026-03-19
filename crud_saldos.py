from database import conectar

def reemplazar_saldos_por_dni(dni, registros):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM saldos_vacacionales WHERE dni = %s", (dni,))

    query = """
    INSERT INTO saldos_vacacionales
    (dni, nombres, periodo_vacacional, dias_maximos, dias_usados, saldo_disponible, fuente_archivo)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    for r in registros:
        cursor.execute(
            query,
            (
                r["dni"],
                r["nombres"],
                r["periodo_vacacional"],
                r["dias_maximos"],
                r["dias_usados"],
                r["saldo_disponible"],
                r["fuente_archivo"]
            )
        )

    conn.commit()
    cursor.close()
    conn.close()

def reemplazar_todos_los_saldos(registros):
    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM saldos_vacacionales")

    query = """
    INSERT INTO saldos_vacacionales
    (dni, nombres, periodo_vacacional, dias_maximos, dias_usados, saldo_disponible, fuente_archivo)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    for r in registros:
        cursor.execute(
            query,
            (
                r["dni"],
                r["nombres"],
                r["periodo_vacacional"],
                r["dias_maximos"],
                r["dias_usados"],
                r["saldo_disponible"],
                r["fuente_archivo"]
            )
        )

    conn.commit()
    cursor.close()
    conn.close()

def obtener_saldos_por_dni(dni):
    conn = conectar()
    cursor = conn.cursor()

    query = """
    SELECT dni, nombres, periodo_vacacional, dias_maximos, dias_usados, saldo_disponible, fuente_archivo
    FROM saldos_vacacionales
    WHERE dni = %s
    ORDER BY periodo_vacacional
    """

    cursor.execute(query, (dni,))
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return [
        {
            "dni": row[0],
            "nombres": row[1],
            "periodo_vacacional": row[2],
            "dias_maximos": row[3],
            "dias_usados": row[4],
            "saldo_disponible": row[5],
            "fuente_archivo": row[6]
        }
        for row in rows
    ]

def validar_saldo_en_db(dni, dias_solicitados, periodo_mencionado=None):
    saldos = obtener_saldos_por_dni(dni)

    if not saldos:
        return False, "No encontré saldo vacacional cargado para ese DNI.", None

    if periodo_mencionado:
        encontrados = [s for s in saldos if s["periodo_vacacional"] == periodo_mencionado]

        if not encontrados:
            disponibles = ", ".join(s["periodo_vacacional"] for s in saldos)
            return False, f"No encontré el período {periodo_mencionado}. Períodos disponibles: {disponibles}.", None

        elegido = encontrados[0]

        if elegido["saldo_disponible"] < dias_solicitados:
            return False, (
                f"No tenés saldo suficiente en el período {elegido['periodo_vacacional']}. "
                f"Saldo disponible: {elegido['saldo_disponible']} días. "
                f"Días solicitados: {dias_solicitados}."
            ), None

        return True, (
            f"Saldo validado en el período {elegido['periodo_vacacional']}. "
            f"Saldo disponible: {elegido['saldo_disponible']} días."
        ), elegido["periodo_vacacional"]

    con_saldo = [s for s in saldos if s["saldo_disponible"] > 0]

    if len(con_saldo) == 0:
        detalle = " | ".join(
            f"{s['periodo_vacacional']}: saldo {s['saldo_disponible']}"
            for s in saldos
        )
        return False, f"No tenés saldo disponible. Detalle: {detalle}.", None

    if len(con_saldo) > 1:
        detalle = " | ".join(
            f"{s['periodo_vacacional']}: saldo {s['saldo_disponible']}"
            for s in con_saldo
        )
        return False, (
            "Tenés saldo en más de un período vacacional. "
            f"Indicá el período en tu mensaje, por ejemplo 2025-2026. Detalle: {detalle}."
        ), None

    elegido = con_saldo[0]

    if elegido["saldo_disponible"] < dias_solicitados:
        return False, (
            f"No tenés saldo suficiente en el período {elegido['periodo_vacacional']}. "
            f"Saldo disponible: {elegido['saldo_disponible']} días. "
            f"Días solicitados: {dias_solicitados}."
        ), None

    return True, (
        f"Saldo validado en el período {elegido['periodo_vacacional']}. "
        f"Saldo disponible: {elegido['saldo_disponible']} días."
    ), elegido["periodo_vacacional"]