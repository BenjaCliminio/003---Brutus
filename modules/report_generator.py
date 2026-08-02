"""
report_generator.py
--------------------
Genera un informe PDF a partir de un ResultadoAtaque, con formato
similar a un informe de pentest real: resumen ejecutivo, estadísticas,
y recomendaciones de política de contraseñas.
"""

from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from modules.attack_engine import ResultadoAtaque


def _generar_recomendaciones(resultado: ResultadoAtaque) -> list:
    recomendaciones = []

    if resultado.credencial_encontrada:
        recomendaciones.append(
            "Se encontró una contraseña débil en menos de "
            f"{resultado.total_intentos} intentos. Se recomienda forzar "
            "una política de contraseñas más estricta (longitud mínima, "
            "combinación de caracteres, verificación contra diccionarios comunes)."
        )
    else:
        recomendaciones.append(
            "No se encontraron credenciales válidas dentro del diccionario "
            "utilizado. Esto no garantiza que la contraseña sea fuerte; "
            "se recomienda repetir la prueba con diccionarios más amplios."
        )

    if resultado.posible_honeypot:
        recomendaciones.append(
            "Se detectaron variaciones anómalas en los tiempos de respuesta, "
            "lo que podría indicar un mecanismo de defensa tipo tarpit o "
            "rate-limiting activo. Esto es una buena práctica de seguridad "
            "del lado del objetivo."
        )

    recomendaciones.append(
        "Implementar bloqueo de cuenta tras N intentos fallidos y "
        "autenticación multifactor (MFA) para reducir el riesgo de "
        "ataques de fuerza bruta, incluso con contraseñas robustas."
    )

    return recomendaciones


def generar_reporte_pdf(resultado: ResultadoAtaque, path_salida: str) -> None:
    doc = SimpleDocTemplate(path_salida, pagesize=A4,
                             topMargin=2 * cm, bottomMargin=2 * cm)
    styles = getSampleStyleSheet()
    titulo_style = ParagraphStyle(
        "Titulo", parent=styles["Title"], fontSize=20, spaceAfter=12
    )
    subtitulo_style = ParagraphStyle(
        "Subtitulo", parent=styles["Heading2"], spaceBefore=16, spaceAfter=8
    )

    elementos = []

    elementos.append(Paragraph("Informe de Auditoría de Contraseñas", titulo_style))
    elementos.append(Paragraph(
        f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}", styles["Normal"]
    ))
    elementos.append(Spacer(1, 0.5 * cm))

    # Resumen ejecutivo
    elementos.append(Paragraph("Resumen Ejecutivo", subtitulo_style))
    resumen_texto = (
        f"Se realizó una prueba de diccionario contra el objetivo "
        f"<b>{resultado.objetivo}</b> utilizando el protocolo "
        f"<b>{resultado.protocolo}</b>. Se probaron "
        f"<b>{resultado.total_intentos}</b> credenciales en "
        f"<b>{resultado.tiempo_total_seg:.2f} segundos</b>."
    )
    elementos.append(Paragraph(resumen_texto, styles["Normal"]))
    elementos.append(Spacer(1, 0.3 * cm))

    # Tabla de resultados clave
    estado_credencial = (
        f"{resultado.credencial_encontrada.password}"
        if resultado.credencial_encontrada else "No encontrada"
    )
    datos_tabla = [
        ["Métrica", "Valor"],
        ["Objetivo", resultado.objetivo],
        ["Protocolo", resultado.protocolo],
        ["Intentos realizados", str(resultado.total_intentos)],
        ["Tiempo total", f"{resultado.tiempo_total_seg:.2f} s"],
        ["Credencial hallada", estado_credencial],
        ["Posible honeypot/tarpit", "Sí" if resultado.posible_honeypot else "No"],
    ]
    tabla = Table(datos_tabla, colWidths=[6 * cm, 8 * cm])
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f2f2f2")]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
    ]))
    elementos.append(tabla)
    elementos.append(Spacer(1, 0.5 * cm))

    # Recomendaciones
    elementos.append(Paragraph("Recomendaciones", subtitulo_style))
    for rec in _generar_recomendaciones(resultado):
        elementos.append(Paragraph(f"• {rec}", styles["Normal"]))
        elementos.append(Spacer(1, 0.15 * cm))

    doc.build(elementos)
    print(f"[+] Informe PDF generado en {path_salida}")