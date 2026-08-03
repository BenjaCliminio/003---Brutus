```
 ____  ____  _   _ _____ _   _ ____
| __ )|  _ \| | | |_   _| | | / ___|
|  _ \| |_) | | | | | | | | | \___ \
| |_) |  _ <| |_| | | | | |_| |___) |
|____/|_| \_\\___/  |_|  \___/|____/
```

# BRUTUS

Herramienta de auditoría de contraseñas que combina generación de diccionarios dirigidos (OSINT), un motor de reglas de mutación configurable, y un ataque de fuerza bruta por diccionario contra servicios SSH o formularios de login HTTP, cerrando el proceso con un informe automático en PDF.

A diferencia de un generador de contraseñas "a ciegas", BRUTUS construye su diccionario a partir de información específica sobre el objetivo, partiendo de la idea de que la mayoría de las contraseñas débiles no son aleatorias, sino que están basadas en datos personales fáciles de inferir (nombres, fechas, mascotas, equipos favoritos, etc.).

---

## ⚠️ Uso ético y legal

Esta herramienta fue desarrollada con **fines educativos y de práctica en ciberseguridad ofensiva** (pentesting, CTFs, laboratorios propios).

**No la uses contra sistemas, cuentas o personas sin autorización explícita.** El acceso no autorizado a sistemas informáticos es un delito en la mayoría de los países. El autor no se responsabiliza por el uso indebido de este software.

---

## 🚀 Funcionalidades

- **Generación de diccionarios dirigidos (OSINT):** a partir de un perfil del objetivo (nombre, apellido, fecha de nacimiento, empresa, mascota, apodos, equipo favorito), genera palabras base personalizadas en vez de depender de listas genéricas.
- **Motor de reglas de mutación configurable (YAML):** expande la wordlist base aplicando leetspeak, sufijos numéricos, capitalización e inversión, con reglas legibles y editables sin tocar el código.
- **Ataque de diccionario multi-protocolo:** arquitectura de plugins que soporta SSH y formularios HTTP, pensada para agregar nuevos protocolos fácilmente.
- **Barra de progreso en tiempo real:** muestra porcentaje completado, velocidad de intentos por segundo y tiempo estimado restante durante el ataque.
- **Detección heurística de honeypot/tarpit:** analiza la varianza en los tiempos de respuesta del objetivo para alertar sobre posibles mecanismos de defensa activos.
- **Informe PDF automático:** genera un reporte tipo pentest con resumen ejecutivo, estadísticas del ataque y recomendaciones de remediación.

---

## 🛠️ Instalación

```bash
pip install -r requirements.txt
```

---

## ▶️ Uso

```bash
python Brutus.py --perfil examples/target_profile_example.yaml --reglas rules/default_rules.yaml --host 127.0.0.1 --puerto 2222 --usuario <usuario> --protocolo ssh --delay 0.2 --salida-pdf informe.pdf
```

### Explicación de cada parámetro

| Parámetro | Obligatorio | Descripción |
|---|---|---|
| `--perfil` | Sí | Ruta al archivo `.yaml` con los datos OSINT del objetivo (nombre, fecha de nacimiento, mascota, etc.). A partir de esto se genera la wordlist base. |
| `--reglas` | Sí | Ruta al archivo `.yaml` con las reglas de mutación que se aplican sobre la wordlist base (leetspeak, sufijos, capitalización, inversión). |
| `--host` | Sí | Dirección IP o dominio del objetivo a auditar. Por ejemplo `127.0.0.1` si estás probando en tu propia máquina, o la IP de una VM/contenedor de laboratorio. |
| `--puerto` | Sí | Puerto donde escucha el servicio a atacar. `22` es el estándar para SSH; para formularios HTTP suele ser `80` o `443`, o el puerto que use tu entorno de prueba. |
| `--usuario` | Sí | Nombre de usuario contra el cual se van a probar las contraseñas generadas (por ejemplo `root`, `admin`, o el usuario que hayas creado en tu entorno de prueba). |
| `--protocolo` | Sí | Protocolo del servicio objetivo. Solo acepta dos valores: `ssh` o `http_form`. |
| `--url-login` | Solo si `--protocolo http_form` | URL completa del endpoint de login del formulario web (ej: `http://192.168.1.50/login`). No se usa con SSH. |
| `--campo-usuario` | No (default: `username`) | Nombre del campo del formulario HTML donde va el usuario. Solo aplica a `http_form`. |
| `--campo-password` | No (default: `password`) | Nombre del campo del formulario HTML donde va la contraseña. Solo aplica a `http_form`. |
| `--texto-error` | No (default: `Invalid`) | Texto que aparece en la respuesta del servidor cuando el login falla. BRUTUS lo usa para distinguir un intento exitoso de uno fallido. Solo aplica a `http_form`. |
| `--delay` | No (default: `0.5`) | Segundos de espera entre cada intento de contraseña. Valores más altos son más lentos pero menos detectables; valores bajos son más rápidos pero más agresivos contra el objetivo. |
| `--salida-pdf` | No (default: `informe.pdf`) | Ruta y nombre del archivo PDF donde se guarda el informe final con los resultados del ataque. |

---

## 📝 Configurar el perfil OSINT (`target_profile_example.yaml`)

Este archivo es el que le da a BRUTUS su ventaja frente a un diccionario genérico: ahí cargás los datos del objetivo que querés auditar, y la herramienta los usa para generar contraseñas candidatas personalizadas.

Abrí `examples/target_profile_example.yaml` con cualquier editor de texto (VS Code, Notepad, etc.) y completá los campos con la información real del objetivo que estés auditando (siempre dentro de un entorno autorizado):

```yaml
nombre: "Juan"
apellido: "Perez"
fecha_nacimiento: "1995-04-12"
empresa: "AcmeCorp"
mascota: "Firulais"
equipo_favorito: "River"
apodos:
  - "juancito"
hijos: []
```

**Qué hace cada campo:**

- **`nombre`** y **`apellido`**: se usan solos, combinados entre sí, y combinados con la fecha de nacimiento (ej: `Juan`, `JuanPerez`, `Juan1995`).
- **`fecha_nacimiento`**: tiene que ir en formato `AAAA-MM-DD`. BRUTUS extrae de acá el año completo, el año corto (dos dígitos) y combinaciones de día/mes, para pegárselos a las demás palabras.
- **`empresa`**: útil si estás auditando una cuenta corporativa — mucha gente usa el nombre de su empresa como parte de la contraseña.
- **`mascota`**: uno de los datos más comunes en contraseñas reales; solo o combinado con años.
- **`equipo_favorito`**: mismo criterio que mascota — un dato personal muy usado como base de contraseña.
- **`apodos`**: lista de sobrenombres conocidos del objetivo. Podés agregar tantos como quieras, cada uno en su propia línea con un guion adelante.
- **`hijos`**: lista de nombres de hijos, si aplica. Si no tenés ese dato o no corresponde, dejalo como lista vacía (`[]`).

Si algún campo no aplica o no tenés ese dato, podés dejarlo vacío (`""`) o eliminarlo — BRUTUS simplemente no va a generar palabras a partir de ese campo faltante, sin romper el resto del proceso.

Podés crear tantos perfiles como objetivos quieras auditar; solo asegurate de pasarle la ruta correcta con `--perfil` al ejecutar la herramienta.

---

