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

#===================================================================
# 02 - Funcion orquestadora principal (Unica funcion del archivo, dentro se divide en sub-bloques.)
#===================================================================

#===================================================================
## Parseo de argumentos (define qué datos necesita el usuario pasar por consola (perfil OSINT, reglas, host, puerto, usuario, protocolo, etc.) y por qué cada uno es necesario.)
#===================================================================

#===================================================================
## Etapa 1 - Generacion de Wordlist base (carga el perfil OSINT y genera las palabras semilla (nombre, apellido, fecha, etc.) sin mutaciones todavía.)
#===================================================================

#===================================================================
## Etapa 2 - Aplicacion de reglas de mutacion (toma la wordlist base y la expande aplicando leetspeak, sufijos, capitalización, etc.)
#===================================================================

#===================================================================
## Etapa 3 - Seleccion del plugin de protocolo (decide si instanciar PluginSSH o PluginHTTPForm según lo que eligió el usuario, y valida que si es HTTP form tenga la URL de login.)
#===================================================================

#===================================================================
## Etapa 4 - Ejecucion del ataque (instancia MotorAtaque con el plugin elegido y corre la wordlist final contra el objetivo.)
#===================================================================

#===================================================================
## Etapa 5 - Reporte de resultado por consola (imprime si se encontró credencial o no, antes de generar el PDF.)
#===================================================================

#===================================================================
## Etapa 6 - Generacion del informe PDF (Llama a generar_reporte_pdf() con el resultado del ataque.)
#===================================================================

#===================================================================
## Punto de entrada - if __name__ == "__main__" (dispara main() solo si el archivo se ejecuta directamente (no si se importa como módulo).)
#===================================================================