from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime, time
from enum import Enum
from typing import Optional

class EstadoReserva(Enum):
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    NO_SHOW = "NO_SHOW"


class EstadoSolicitud(Enum):
    PENDIENTE = "PENDIENTE"
    APROBADA = "APROBADA"
    RECHAZADA = "RECHAZADA"


class EstadoConflicto(Enum):
    ABIERTO = "ABIERTO"
    EN_REVISION = "EN_REVISION"
    ATENDIDO = "ATENDIDO"

class ReglaPrioridad(ABC):

    @abstractmethod
    def permite_reservar(self, hora: time) -> bool:
        pass

    @abstractmethod
    def nivel_prioridad(self) -> int:
        pass


class SinPrioridad(ReglaPrioridad):

    def permite_reservar(self, hora: time) -> bool:
        # Un estudiante regular solamente puede reservar desde las 18:00.
        return hora >= time(18, 0)

    def nivel_prioridad(self) -> int:
        return 0


class PrioridadAntesDeLas18(ReglaPrioridad):

    def permite_reservar(self, hora: time) -> bool:
        # El capitán puede reservar antes y después de las 18:00.
        return True

    def nivel_prioridad(self) -> int:
        return 1

# ESTUDIANTES
class Estudiante:

    def __init__(self,id_estudiante: str,nombre: str,regla_prioridad: ReglaPrioridad):
        self.id = id_estudiante
        self.nombre = nombre
        self.regla_prioridad = regla_prioridad
        self.reservas: list[Reserva] = []

    def puede_reservar(self, hora: time) -> bool:
        return self.regla_prioridad.permite_reservar(hora)

    def agregar_reserva(self, reserva: Reserva) -> None:
        self.reservas.append(reserva)

    def es_propietario(self, reserva: Reserva) -> bool:
        return reserva.estudiante is self

    def __str__(self) -> str:
        return self.nombre


class Capitan(Estudiante):

    def __init__(self,id_estudiante: str,nombre: str,equipo_oficial: str):
        super().__init__(
            id_estudiante,
            nombre,
            PrioridadAntesDeLas18()
        )
        self.equipo_oficial = equipo_oficial

# CUENTA INSTITUCIONAL
class CuentaInstitucional:

    def __init__(self,identificador: str,contrasena: str,propietario: Estudiante,activa: bool = True):
        self.identificador = identificador
        self.contrasena = contrasena
        self.activa = activa
        self.propietario = propietario

    def autenticar(self, contrasena: str) -> bool:
        return self.activa and self.contrasena == contrasena

    def obtener_propietario(self) -> Estudiante:
        return self.propietario

# CANCHA
class Cancha:

    def __init__(self,id_cancha: str,nombre: str,habilitada: bool = True):
        self.id = id_cancha
        self.nombre = nombre
        self.habilitada = habilitada
        self.reservas: list[Reserva] = []

    def esta_disponible(self,fecha: date,hora: time) -> bool:

        if not self.habilitada:
            return False

        for reserva in self.reservas:
            if (
                reserva.fecha == fecha
                and reserva.hora_inicio == hora
                and reserva.estado == EstadoReserva.CONFIRMADA
            ):
                return False
        return True
    def agregar_reserva(self, reserva: Reserva) -> None:
        self.reservas.append(reserva)

    def habilitar(self) -> None:
        self.habilitada = True

    def inhabilitar(self) -> None:
        self.habilitada = False

    def __str__(self) -> str:
        estado = "Habilitada" if self.habilitada else "Inhabilitada"
        return f"{self.nombre} ({estado})"

# SOLICITUD DE RESERVA
class SolicitudReserva:

    def __init__(self,id_solicitud: str,solicitante: Estudiante,cancha: Cancha,fecha: date,hora_inicio: time,momento_recepcion: Optional[datetime] = None):
        self.id = id_solicitud
        self.solicitante = solicitante
        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.momento_recepcion = (
            momento_recepcion
            if momento_recepcion is not None
            else datetime.now()
        )
        self.estado = EstadoSolicitud.PENDIENTE

    def coincide_con(self, otra: SolicitudReserva) -> bool:
        return (
            self.cancha is otra.cancha
            and self.fecha == otra.fecha
            and self.hora_inicio == otra.hora_inicio
        )

    def aprobar(self) -> None:
        self.estado = EstadoSolicitud.APROBADA

    def rechazar(self) -> None:
        self.estado = EstadoSolicitud.RECHAZADA

# RESERVA
class Reserva:

    def __init__(self,id_reserva: str,estudiante: Estudiante,cancha: Cancha,fecha: date,hora_inicio: time):
        self.id = id_reserva
        self.estudiante = estudiante
        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.estado = EstadoReserva.CONFIRMADA

    def pertenece_a(self, estudiante: Estudiante) -> bool:
        return self.estudiante is estudiante

    def fecha_hora_inicio(self) -> datetime:
        return datetime.combine(
            self.fecha,
            self.hora_inicio
        )

    def calcular_tiempo_restante(self,momento_actual: datetime):
        return self.fecha_hora_inicio() - momento_actual
    def cancelar(self,estudiante: Estudiante,momento_actual: datetime) -> EstadoReserva:
        if not self.pertenece_a(estudiante):
            raise PermissionError(
                "El estudiante no puede cancelar una reserva que no le pertenece."
            )
        tiempo_restante = self.calcular_tiempo_restante(
            momento_actual
        )
        # Dos horas o más:
        if tiempo_restante.total_seconds() >= 2 * 60 * 60:
            self.estado = EstadoReserva.CANCELADA
        # Menos de dos horas:
        else:
            self.estado = EstadoReserva.NO_SHOW

        return self.estado
    def __str__(self) -> str:
        return (
            f"Reserva {self.id}: "
            f"{self.cancha.nombre} | "
            f"{self.fecha} | "
            f"{self.hora_inicio.strftime('%H:%M')} | "
            f"{self.estado.value}"
        )
# CONFLICTO ADMINISTRATIVO
class ConflictoAdministrativo:

    def __init__(
        self,id_conflicto: str,descripcion: str,reservas: list[Reserva]):
        self.id = id_conflicto
        self.descripcion = descripcion
        self.reservas = reservas
        self.estado = EstadoConflicto.ABIERTO
        self.intervenciones: list[str] = []

    def marcar_en_revision(self) -> None:
        self.estado = EstadoConflicto.EN_REVISION

    def registrar_intervencion(
        self,
        administrador: Administrador
    ) -> None:

        self.marcar_en_revision()

        self.intervenciones.append(
            f"Intervención registrada por {administrador.nombre}"
        )
        self.estado = EstadoConflicto.ATENDIDO
    def __str__(self) -> str:
        return (
            f"{self.id} - {self.descripcion} "
            f"[{self.estado.value}]"
        )

# ADMINISTRADOR

class Administrador:
    def __init__(self,id_administrador: str,nombre: str):
        self.id = id_administrador
        self.nombre = nombre

    def registrar_cancha(self,gestor,cancha: Cancha) -> None:
        gestor.registrar_cancha(cancha)

    def habilitar_cancha(self, cancha: Cancha) -> None:
        cancha.habilitar()

    def inhabilitar_cancha(self,cancha: Cancha) -> None:
        cancha.inhabilitar()

    def consultar_conflictos(self,conflictos: list[ConflictoAdministrativo]) -> list[ConflictoAdministrativo]:
        return conflictos

    def intervenir_conflicto(self,conflicto: ConflictoAdministrativo) -> None:
        conflicto.registrar_intervencion(self)