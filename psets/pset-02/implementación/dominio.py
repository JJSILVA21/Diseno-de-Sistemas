from __future__ import annotations

from abc import ABC, abstractmethod
from copy import deepcopy
from datetime import date, datetime, timedelta, time
from enum import Enum

from configuracion import ConfiguracionReservaU


class EstadoReserva(Enum):
    CONFIRMADA = "CONFIRMADA"
    CANCELADA = "CANCELADA"
    NO_SHOW = "NO_SHOW"
    ANULADA_ADMINISTRATIVAMENTE = "ANULADA_ADMINISTRATIVAMENTE"


class ReglaPrioridad(ABC):
    @abstractmethod
    def permite_reservar(self, hora):
        pass


class SinPrioridad(ReglaPrioridad):
    def permite_reservar(self, hora):
        configuracion = ConfiguracionReservaU.obtener_instancia()
        return hora >= configuracion.hora_prioridad


class PrioridadAntesDeLas18(ReglaPrioridad):
    def permite_reservar(self, hora):
        return True


class PoliticaCancelacion(ABC):
    @abstractmethod
    def cancelar(self, reserva, momento_actual):
        pass


class PoliticaCancelacionEstudiante(PoliticaCancelacion):
    def cancelar(self, reserva, momento_actual):
        configuracion = ConfiguracionReservaU.obtener_instancia()
        limite = timedelta(hours=configuracion.cancelacion_estudiante_horas)

        if reserva.fecha_hora_inicio() - momento_actual >= limite:
            reserva.estado = EstadoReserva.CANCELADA
        else:
            reserva.estado = EstadoReserva.NO_SHOW
            reserva.fecha_no_show = momento_actual
            reserva.solicitante.evaluar_suspension(momento_actual)

        return reserva.estado


class PoliticaCancelacionCapitan(PoliticaCancelacion):
    def cancelar(self, reserva, momento_actual):
        configuracion = ConfiguracionReservaU.obtener_instancia()
        limite = timedelta(hours=configuracion.cancelacion_capitan_horas)

        if reserva.fecha_hora_inicio() - momento_actual >= limite:
            reserva.estado = EstadoReserva.CANCELADA
        else:
            reserva.estado = EstadoReserva.NO_SHOW
            reserva.fecha_no_show = momento_actual
            reserva.solicitante.evaluar_suspension(momento_actual)

        return reserva.estado


class PoliticaAnulacionAdministrativa(PoliticaCancelacion):
    def cancelar(self, reserva, momento_actual):
        reserva.estado = EstadoReserva.ANULADA_ADMINISTRATIVAMENTE
        return reserva.estado


class Sede:
    def __init__(self, id_sede, nombre):
        self.id = id_sede
        self.nombre = nombre


class Cancha:
    def __init__(self, id_cancha, nombre, sede, habilitada=True):
        self.id = id_cancha
        self.nombre = nombre
        self.sede = sede
        self.habilitada = habilitada

    def habilitar(self):
        self.habilitada = True

    def inhabilitar(self):
        self.habilitada = False


class Suspension:
    def __init__(self, fecha_inicio, fecha_fin):
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin

    def esta_vigente(self, momento):
        return self.fecha_inicio <= momento < self.fecha_fin


class Estudiante:
    def __init__(self, id_estudiante, nombre, correo):
        self.id = id_estudiante
        self.nombre = nombre
        self.correo = correo
        self.regla_prioridad = SinPrioridad()
        self.reservas = []
        self.suspensiones = []

    def puede_reservar(self, hora):
        return self.regla_prioridad.permite_reservar(hora)

    def agregar_reserva(self, reserva):
        self.reservas.append(reserva)

    def contar_no_shows(self, momento):
        return sum(
            reserva.estado == EstadoReserva.NO_SHOW
            and reserva.fecha_no_show is not None
            and reserva.fecha_no_show.year == momento.year
            and reserva.fecha_no_show.month == momento.month
            for reserva in self.reservas
        )

    def esta_suspendido(self, momento):
        return any(
            suspension.esta_vigente(momento)
            for suspension in self.suspensiones
        )

    def evaluar_suspension(self, momento):
        configuracion = ConfiguracionReservaU.obtener_instancia()

        ya_tiene_suspension = any(
            suspension.fecha_inicio.year == momento.year
            and suspension.fecha_inicio.month == momento.month
            for suspension in self.suspensiones
        )

        if (
            self.contar_no_shows(momento) >= configuracion.limite_no_shows
            and not ya_tiene_suspension
        ):
            suspension = Suspension(
                momento,
                momento + timedelta(days=configuracion.dias_suspension)
            )
            self.suspensiones.append(suspension)
            return suspension

        return None


class Capitan(Estudiante):
    def __init__(self, id_estudiante, nombre, correo, equipo_oficial):
        super().__init__(id_estudiante, nombre, correo)
        self.equipo_oficial = equipo_oficial
        self.regla_prioridad = PrioridadAntesDeLas18()


class Administrador:
    def __init__(self, id_administrador, nombre):
        self.id = id_administrador
        self.nombre = nombre


class Reserva:
    def __init__(
        self,
        id_reserva,
        solicitante,
        cancha,
        fecha,
        hora_inicio,
        hora_fin,
        politica_cancelacion
    ):
        self.id = id_reserva
        self.solicitante = solicitante
        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.politica_cancelacion = politica_cancelacion
        self.estado = EstadoReserva.CONFIRMADA
        self.fecha_no_show = None

    def pertenece_a(self, solicitante):
        return self.solicitante is solicitante

    def fecha_hora_inicio(self):
        return datetime.combine(self.fecha, self.hora_inicio)

    def cancelar(self, solicitante, momento_actual):
        if not self.pertenece_a(solicitante):
            raise PermissionError("La reserva no pertenece al solicitante.")

        if self.estado != EstadoReserva.CONFIRMADA:
            raise ValueError("La reserva ya no puede cambiar de estado.")

        return self.politica_cancelacion.cancelar(self, momento_actual)


class ReservaRegular(Reserva):
    pass


class ReservaEquipoOficial(Reserva):
    pass


class ReservaRecurrente:
    def __init__(
        self,
        cancha,
        fecha_inicio,
        hora_inicio,
        hora_fin,
        solicitante,
        numero_semanas,
        equipo_prestado,
        notas
    ):
        self.cancha = cancha
        self.fecha_inicio = fecha_inicio
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.solicitante = solicitante
        self.numero_semanas = numero_semanas
        self.equipo_prestado = equipo_prestado
        self.notas = notas
        self.reservas = []


class ReservaRecurrenteBuilder:
    def __init__(
        self,
        cancha,
        fecha_inicio,
        hora_inicio,
        hora_fin,
        solicitante
    ):
        self.cancha = cancha
        self.fecha_inicio = fecha_inicio
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.solicitante = solicitante
        self.numero_semanas = 2
        self.equipo_prestado = []
        self.notas = ""

    def con_numero_semanas(self, numero_semanas):
        self.numero_semanas = numero_semanas
        return self

    def con_equipo_prestado(self, equipo_prestado):
        self.equipo_prestado = equipo_prestado
        return self

    def con_notas(self, notas):
        self.notas = notas
        return self

    def build(self):
        if not isinstance(self.solicitante, Capitan):
            raise ValueError("Solo un capitán puede crear una reserva recurrente.")

        if not 2 <= self.numero_semanas <= 8:
            raise ValueError("La reserva recurrente debe tener entre 2 y 8 semanas.")

        return ReservaRecurrente(
            self.cancha,
            self.fecha_inicio,
            self.hora_inicio,
            self.hora_fin,
            self.solicitante,
            self.numero_semanas,
            self.equipo_prestado,
            self.notas
        )

class Bloqueo:
    def __init__(
        self,
        id_bloqueo,
        motivo,
        hora_inicio,
        hora_fin,
        equipo
    ):
        self.id = id_bloqueo
        self.motivo = motivo
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.equipo = equipo
        self.cancha = None
        self.fecha = None

    def clonar(self, cancha, fecha):
        clon = deepcopy(self)
        clon.cancha = cancha
        clon.fecha = fecha
        return clon