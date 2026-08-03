"""
osint_wordlist.py
------------------
Genera una wordlist base a partir de información OSINT recolectada
sobre un objetivo (nombre, apellido, fecha de nacimiento, empresa,
mascota, apodos, redes sociales, etc.).

Esta es la diferenciación principal frente a herramientas como Hydra
o John the Ripper, que solo consumen diccionarios estáticos: acá el
diccionario se construye de forma dirigida al objetivo.

Uso: pensado para auditorías de contraseñas autorizadas (labs propios,
entornos de test, o pentests con autorización explícita).
"""

from itertools import product
from typing import Dict, List, Set
import yaml


def cargar_perfil(path_yaml: str) -> Dict:
    """Carga el perfil OSINT del objetivo desde un archivo YAML."""
    with open(path_yaml, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def _extraer_anios(fecha_nacimiento: str) -> List[str]:
    """
    A partir de una fecha (YYYY-MM-DD), extrae variantes numéricas
    comunes usadas en contraseñas: año completo, año corto, día+mes, etc.
    """
    if not fecha_nacimiento:
        return []
    partes = fecha_nacimiento.split("-")
    if len(partes) != 3:
        return []
    anio, mes, dia = partes
    variantes = {
        anio,
        anio[-2:],
        f"{dia}{mes}",
        f"{mes}{dia}",
        f"{dia}{mes}{anio}",
        f"{dia}{mes}{anio[-2:]}",
    }
    return list(variantes)


def generar_wordlist_base(perfil: Dict) -> Set[str]:
    """
    Genera palabras base combinando los distintos campos del perfil.
    No aplica mutaciones todavía (eso lo hace rules_engine.py) — acá
    solo se generan las "semillas".
    """
    palabras: Set[str] = set()

    nombre = perfil.get("nombre", "")
    apellido = perfil.get("apellido", "")
    apodos = perfil.get("apodos", [])
    empresa = perfil.get("empresa", "")
    mascota = perfil.get("mascota", "")
    hijos = perfil.get("hijos", [])
    equipo_favorito = perfil.get("equipo_favorito", "")
    fecha_nacimiento = perfil.get("fecha_nacimiento", "")

    campos_simples = [nombre, apellido, empresa, mascota, equipo_favorito]
    campos_simples += apodos + hijos

    for campo in campos_simples:
        if campo:
            palabras.add(campo.lower())
            palabras.add(campo.capitalize())

    # Combinaciones nombre + apellido (muy comunes como usuario/contraseña base)
    if nombre and apellido:
        combinaciones = [
            f"{nombre}{apellido}",
            f"{apellido}{nombre}",
            f"{nombre[0]}{apellido}",
            f"{nombre}{apellido[0]}",
        ]
        for c in combinaciones:
            palabras.add(c.lower())
            palabras.add(c.capitalize())

    # Combinaciones palabra + año/fecha
    anios = _extraer_anios(fecha_nacimiento)
    base_words = list(palabras)
    for palabra, anio in product(base_words, anios):
        palabras.add(f"{palabra}{anio}")

    return palabras


def guardar_wordlist(palabras: Set[str], path_salida: str) -> None:
    with open(path_salida, "w", encoding="utf-8") as f:
        for palabra in sorted(palabras):
            f.write(palabra + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 3:
        print("Uso: python osint_wordlist.py <perfil.yaml> <salida.txt>")
        sys.exit(1)

    perfil = cargar_perfil(sys.argv[1])
    palabras = generar_wordlist_base(perfil)
    guardar_wordlist(palabras, sys.argv[2])
    print(Fore.GREEN + f"[+] {len(wordlist_base)} palabras base generadas")