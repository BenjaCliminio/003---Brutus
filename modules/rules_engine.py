"""
rules_engine.py
----------------
Motor de mutación de palabras basado en reglas configurables en YAML.
Pensado para ser más legible que la sintaxis de Hashcat, sin perder
flexibilidad.

Reglas soportadas (ver rules/default_rules.yaml):
  - leetspeak: sustituye vocales por números (a->4, e->3, i->1, o->0)
  - capitalizar: pone la primera letra en mayúscula
  - sufijos: agrega una lista de sufijos (ej: '123', '!', '2024')
  - prefijos: agrega una lista de prefijos
  - invertir: invierte la palabra
"""

from typing import Dict, List, Set
import yaml

LEET_MAP = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5"}


def cargar_reglas(path_yaml: str) -> Dict:
    with open(path_yaml, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def aplicar_leetspeak(palabra: str) -> str:
    return "".join(LEET_MAP.get(c, c) for c in palabra)


def aplicar_reglas(palabras: Set[str], reglas: Dict) -> Set[str]:
    """
    Aplica el set de reglas sobre cada palabra base y devuelve
    el conjunto expandido de candidatos.
    """
    resultado: Set[str] = set(palabras)

    if reglas.get("capitalizar", False):
        resultado |= {p.capitalize() for p in palabras}

    if reglas.get("leetspeak", False):
        resultado |= {aplicar_leetspeak(p) for p in palabras}
        resultado |= {aplicar_leetspeak(p.capitalize()) for p in palabras}

    if reglas.get("invertir", False):
        resultado |= {p[::-1] for p in palabras}

    sufijos: List[str] = reglas.get("sufijos", [])
    if sufijos:
        nuevas = set()
        for p in resultado:
            for s in sufijos:
                nuevas.add(f"{p}{s}")
        resultado |= nuevas

    prefijos: List[str] = reglas.get("prefijos", [])
    if prefijos:
        nuevas = set()
        for p in resultado:
            for pre in prefijos:
                nuevas.add(f"{pre}{p}")
        resultado |= nuevas

    return resultado


def cargar_wordlist(path_txt: str) -> Set[str]:
    with open(path_txt, "r", encoding="utf-8") as f:
        return {line.strip() for line in f if line.strip()}


def guardar_wordlist(palabras: Set[str], path_salida: str) -> None:
    with open(path_salida, "w", encoding="utf-8") as f:
        for palabra in sorted(palabras):
            f.write(palabra + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Uso: python rules_engine.py <wordlist_base.txt> <reglas.yaml> <salida.txt>")
        sys.exit(1)

    palabras = cargar_wordlist(sys.argv[1])
    reglas = cargar_reglas(sys.argv[2])
    expandida = aplicar_reglas(palabras, reglas)
    guardar_wordlist(expandida, sys.argv[3])
    print(f"[+] Wordlist expandida de {len(palabras)} a {len(expandida)} candidatos -> {sys.argv[3]}")