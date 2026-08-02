____  ____  _   _ _____ _   _ ____  
| __ )|  _ \| | | |_   _| | | / ___| 
|  _ \| |_) | | | | | | | | | \___ \ 
| |_) |  _ <| |_| | | | | |_| |___) |
|____/|_| \_\\___/  |_|  \___/|____/

Definicion
BRUTUS es una herramienta de línea de comandos para auditoría de contraseñas que combina generación de diccionarios dirigidos, mutación de palabras y ataque de fuerza bruta por diccionario, cerrando el proceso con un informe automático en PDF. A diferencia de los generadores de contraseñas "a ciegas", BRUTUS construye su diccionario a partir de información específica sobre el objetivo, siguiendo la lógica de que la mayoría de las contraseñas débiles no son aleatorias, sino que están basadas en datos personales fáciles de inferir (nombres, fechas, mascotas, equipos favoritos, etc.).

==============================================================================================================================================
⚠️ Uso ético y legal

Esta herramienta fue desarrollada con fines educativos y de práctica en ciberseguridad ofensiva (pentesting, CTFs, laboratorios propios).
No la uses contra sistemas, cuentas o personas sin autorización explícita. El acceso no autorizado a sistemas informáticos es un delito en la mayoría de los países. El autor no se responsabiliza por el uso indebido de este software.

=============================================================================================================================================
🚀 Funcionalidades
- Generación de diccionarios dirigidos (OSINT): a partir de un perfil del objetivo (nombre, apellido, fecha de nacimiento, empresa, mascota, apodos, equipo favorito), genera palabras base personalizadas en vez de depender de listas genéricas.

- Motor de reglas de mutación configurable (YAML): expande la wordlist base aplicando leetspeak, sufijos numéricos, capitalización e inversión, con reglas legibles y editables sin tocar el código.

- Ataque de diccionario multi-protocolo: arquitectura de plugins que soporta SSH y formularios HTTP, pensada para agregar nuevos protocolos fácilmente.

- Detección heurística de honeypot/tarpit: analiza la varianza en los tiempos de respuesta del objetivo para alertar sobre posibles mecanismos de defensa activos.

- Informe PDF automático: genera un reporte tipo pentest con resumen ejecutivo, estadísticas del ataque y recomendaciones de remediación.

=============================================================================================================================================
🛠️ Instalación

pip install -r requirements.txt

=============================================================================================================================================
▶️ Uso

Contra un servicio SSH:

bash
python Brutus.py \
  --perfil examples/target_profile_example.yaml \
  --reglas rules/default_rules.yaml \
  --host 192.168.1.50 \
  --puerto 22 \
  --usuario juan \
  --protocolo ssh \
  --delay 0.5 \
  --salida-pdf informe.pdf

Contra un formulario de login HTTP:

bash
python Brutus.py \
  --perfil examples/target_profile_example.yaml \
  --reglas rules/default_rules.yaml \
  --host 192.168.1.50 \
  --puerto 80 \
  --usuario juan \
  --protocolo http_form \
  --url-login http://192.168.1.50/login \
  --campo-usuario username \
  --campo-password password \
  --texto-error "Invalid credentials" \
  --salida-pdf informe.pdf

"""