"""
Brutus.py
---------
Orquestador principal de BRUTUS — herramienta de auditoría de
contraseñas basada en OSINT.

Flujo completo:
  1. Genera wordlist base desde perfil OSINT (osint_wordlist.py)
  2. Aplica reglas de mutación (rules_engine.py)
  3. Ejecuta el ataque de diccionario (attack_engine.py)
  4. Genera el informe PDF (report_generator.py)

USO EXCLUSIVO en entornos autorizados: laboratorios propios,
máquinas de práctica (VulnHub, HackTheBox, DVWA, etc.) o pentests
con consentimiento explícito por escrito del propietario del sistema.
"""

# ============================================================
# 01 - BLOQUE DE IMPORTS
# ============================================================
# argparse: para leer los parámetros que el usuario pasa por consola
# colorama: para que los mensajes de consola salgan con color
# modules.*: los cuatro componentes que arman cada etapa del flujo
import argparse
from colorama import init, Fore, Style

from modules.osint_wordlist import cargar_perfil, generar_wordlist_base
from modules.rules_engine import cargar_reglas, aplicar_reglas
from modules.attack_engine import MotorAtaque, PluginSSH, PluginHTTPForm
from modules.report_generator import generar_reporte_pdf

init(autoreset=True)

VERSION = "1.0.0"

# Banner ASCII mostrado al iniciar (estilo Hydra / John the Ripper)
BANNER = r"""
 ____  ____  _   _ _____ _   _ ____
| __ )|  _ \| | | |_   _| | | / ___|
|  _ \| |_) | | | | | | | | | \___ \
| |_) |  _ <| |_| | | | | |_| |___) |
|____/|_| \_\\___/  |_|  \___/|____/
"""


def mostrar_banner():
    """Imprime el banner de bienvenida con datos básicos de la herramienta."""
    print(Fore.RED + Style.BRIGHT + BANNER)
    print(Fore.CYAN + f"  BRUTUS v{VERSION} — Auditoría de contraseñas basada en OSINT")
    print(Fore.YELLOW + "  Uso exclusivo en entornos autorizados (labs propios, CTFs, pentests con consentimiento)")
    print(Fore.WHITE + "-" * 70)


# ============================================================
# 02 - FUNCION ORQUESTADORA PRINCIPAL
# ============================================================
def main():
    mostrar_banner()

    # ------------------------------------------------------------
    # Parseo de argumentos
    # ------------------------------------------------------------
    parser = argparse.ArgumentParser(
        description="BRUTUS — Herramienta de auditoría de contraseñas basada en OSINT (uso autorizado únicamente)"
    )
    parser.add_argument("--perfil", required=True, help="Archivo YAML con el perfil OSINT del objetivo")
    parser.add_argument("--reglas", required=True, help="Archivo YAML con las reglas de mutación")
    parser.add_argument("--host", required=True, help="Host del objetivo (IP o dominio)")
    parser.add_argument("--puerto", type=int, required=True, help="Puerto del servicio")
    parser.add_argument("--usuario", required=True, help="Usuario a probar")
    parser.add_argument("--protocolo", choices=["ssh", "http_form"], required=True)
    parser.add_argument("--url-login", help="URL de login (solo para http_form)")
    parser.add_argument("--campo-usuario", default="username", help="Nombre del campo usuario (http_form)")
    parser.add_argument("--campo-password", default="password", help="Nombre del campo password (http_form)")
    parser.add_argument("--texto-error", default="Invalid", help="Texto que indica login fallido (http_form)")
    parser.add_argument("--delay", type=float, default=0.5, help="Segundos de espera entre intentos")
    parser.add_argument("--salida-pdf", default="informe.pdf", help="Ruta del informe PDF de salida")

    args = parser.parse_args()

    # ------------------------------------------------------------
    # Etapa 1 - Generación de wordlist base
    # ------------------------------------------------------------
    print(Fore.CYAN + "[*] Generando wordlist base desde perfil OSINT...")
    perfil = cargar_perfil(args.perfil)
    wordlist_base = generar_wordlist_base(perfil)
    print(Fore.GREEN + f"[+] {len(wordlist_base)} palabras base generadas")

    # ------------------------------------------------------------
    # Etapa 2 - Aplicación de reglas de mutación
    # ------------------------------------------------------------
    print(Fore.CYAN + "[*] Aplicando reglas de mutación...")
    reglas = cargar_reglas(args.reglas)
    wordlist_final = aplicar_reglas(wordlist_base, reglas)
    print(Fore.GREEN + f"[+] Wordlist final: {len(wordlist_final)} candidatos")

    # ------------------------------------------------------------
    # Etapa 3 - Selección del plugin de protocolo
    # ------------------------------------------------------------
    if args.protocolo == "ssh":
        plugin = PluginSSH()
    else:
        if not args.url_login:
            parser.error("--url-login es requerido para protocolo http_form")
        plugin = PluginHTTPForm(
            url_login=args.url_login,
            campo_usuario=args.campo_usuario,
            campo_password=args.campo_password,
            texto_error=args.texto_error,
        )

    # ------------------------------------------------------------
    # Etapa 4 - Ejecución del ataque
    # ------------------------------------------------------------
    print(Fore.CYAN + f"[*] Ejecutando ataque de diccionario contra {args.host}:{args.puerto} ({args.protocolo})...")
    motor = MotorAtaque(plugin, args.host, args.puerto, delay_seg=args.delay)
    resultado = motor.ejecutar(args.usuario, sorted(wordlist_final))

    # ------------------------------------------------------------
    # Etapa 5 - Reporte de resultado por consola
    # ------------------------------------------------------------
    if resultado.credencial_encontrada:
        print(Fore.GREEN + f"[!] Credencial encontrada: {resultado.credencial_encontrada.password}")
    else:
        print(Fore.RED + "[-] No se encontró ninguna credencial válida en la wordlist")

    # ------------------------------------------------------------
    # Etapa 6 - Generación del informe PDF
    # ------------------------------------------------------------
    print(Fore.CYAN + "[*] Generando informe PDF...")
    generar_reporte_pdf(resultado, args.salida_pdf)


# ============================================================
# PUNTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    main()