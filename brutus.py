# B.R.U.T.U.S (Desarrollada por BSEC)
# ------------
# Orquestador principal de BRUTUS — herramienta de auditoría de contraseñas basada en OSINT.

# Flujo completo:
  # 1. Genera wordlist base desde perfil OSINT (osint_wordlist.py)
  # 2. Aplica reglas de mutación (rules_engine.py)
  # 3. Ejecuta el ataque de diccionario (attack_engine.py)
  # 4. Genera el informe PDF (report_generator.py)

#USO EXCLUSIVO en entornos autorizados: laboratorios propios, máquinas de práctica (VulnHub, HackTheBox, DVWA, etc.) o pentests con consentimiento explícito por escrito del propietario del sistema.


# ==================================================================
# 01 - Bloque de Imports (Qué trae cada módulo (OSINT, reglas, ataque, reporte) y por qué.)
#===================================================================
import argparse

from modules.osint_wordlist import cargar_perfil, generar_wordlist_base
from modules.rules_engine import cargar_reglas, aplicar_reglas
from modules.attack_engine import MotorAtaque, PluginSSH, PluginHTTPForm
from modules.report_generator import generar_reporte_pdf
from colorama import init, Fore, Style

init(autoreset=True)

#===================================================================
# 02 - Funcion orquestadora principal (Unica funcion del archivo, dentro se divide en sub-bloques.)
#===================================================================
def main():
#===================================================================
## Parseo de argumentos (define qué datos necesita el usuario pasar por consola (perfil OSINT, reglas, host, puerto, usuario, protocolo, etc.) y por qué cada uno es necesario.)
#===================================================================
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
#===================================================================
## Etapa 1 - Generacion de Wordlist base (carga el perfil OSINT y genera las palabras semilla (nombre, apellido, fecha, etc.) sin mutaciones todavía.)
#===================================================================
    print(Fore.CYAN + "[*] Generando wordlist base desde perfil OSINT...")
    perfil = cargar_perfil(args.perfil)
    wordlist_base = generar_wordlist_base(perfil)
    print(f"[+] {len(wordlist_base)} palabras base generadas")

#===================================================================
## Etapa 2 - Aplicacion de reglas de mutacion (toma la wordlist base y la expande aplicando leetspeak, sufijos, capitalización, etc.)
#===================================================================
    print(Fore.CYAN + "[*] Aplicando reglas de mutación...")
    reglas = cargar_reglas(args.reglas)
    wordlist_final = aplicar_reglas(wordlist_base, reglas)
    print(f"[+] Wordlist final: {len(wordlist_final)} candidatos")

# ------------------------------------------------------------
    # Etapa 3 - Selección del plugin de protocolo (decide si usar
    # PluginSSH o PluginHTTPForm según lo que eligió el usuario)
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
    # Etapa 4 - Ejecución del ataque (instancia el MotorAtaque con
    # el plugin elegido y corre la wordlist final contra el objetivo)
    # ------------------------------------------------------------
    print(f"[*] Ejecutando ataque de diccionario contra {args.host}:{args.puerto} ({args.protocolo})...")
    motor = MotorAtaque(plugin, args.host, args.puerto, delay_seg=args.delay)
    resultado = motor.ejecutar(args.usuario, sorted(wordlist_final))

    # ------------------------------------------------------------
    # Etapa 5 - Reporte de resultado por consola
    # ------------------------------------------------------------
    if resultado.credencial_encontrada:
        print(f"[!] Credencial encontrada: {resultado.credencial_encontrada.password}")
    else:
        print("[-] No se encontró ninguna credencial válida en la wordlist")

    # ------------------------------------------------------------
    # Etapa 6 - Generación del informe PDF (arma el reporte final
    # con resumen ejecutivo, estadísticas y recomendaciones)
    # ------------------------------------------------------------
    print("[*] Generando informe PDF...")
    generar_reporte_pdf(resultado, args.salida_pdf)


# ============================================================
# PUNTO DE ENTRADA
# ============================================================
if __name__ == "__main__":
    main()