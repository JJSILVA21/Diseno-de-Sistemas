from datetime import date, datetime

from configuracion import ConfiguracionReservaU
from dominio import (
    Administrador,
    EstadoReserva,
    PoliticaAnulacionAdministrativa,
)
from fabricas import FabricaSedes
from gestor_reservas import GestorReservas


class ReservaUFacade:
    def __init__(self):
        self.configuracion = ConfiguracionReservaU.obtener_instancia()
        self.gestor = GestorReservas()

    def registrar_cancha(self, cancha):
        self.gestor.registrar_cancha(cancha)

    def obtener_momento(self, momento_actual):
        if momento_actual is None:
            return datetime.now()

        return momento_actual

    def validar_reserva(
        self,
        solicitante,
        cancha,
        fecha,
        hora_inicio,
        hora_fin,
        momento_actual
    ):
        momento = self.obtener_momento(momento_actual)

        if fecha < date.today():
            raise ValueError("No se pueden crear reservas para una fecha pasada.")

        if solicitante.esta_suspendido(momento):
            raise ValueError("El solicitante está suspendido.")

        if not cancha.habilitada:
            raise ValueError("La cancha está inhabilitada.")

        fabrica_sede = FabricaSedes.obtener(cancha.sede)
        validador = fabrica_sede.crear_validador_horario()

        if not validador.esta_permitido(hora_inicio, hora_fin):
            raise ValueError("El horario no está permitido para la sede.")

        if not solicitante.puede_reservar(hora_inicio):
            raise ValueError(
                "El estudiante regular solo puede reservar desde las 18:00."
            )

    def notificar(self, solicitante, cancha, mensaje):
        fabrica_sede = FabricaSedes.obtener(cancha.sede)
        notificador = fabrica_sede.crear_notificador()
        notificador.notificar(solicitante, mensaje)

    def reservar(
        self,
        solicitante,
        cancha,
        fecha,
        hora_inicio,
        hora_fin,
        momento_actual=None
    ):
        self.validar_reserva(
            solicitante,
            cancha,
            fecha,
            hora_inicio,
            hora_fin,
            momento_actual
        )
        reserva = self.gestor.confirmar_reserva(
            solicitante,
            cancha,
            fecha,
            hora_inicio,
            hora_fin
        )

        self.notificar(
            solicitante,
            cancha,
            f"Reserva {reserva.id} confirmada."
        )

        return reserva

    def reservar_recurrente(self, reserva_recurrente, momento_actual=None):
        self.validar_reserva(
            reserva_recurrente.solicitante,
            reserva_recurrente.cancha,
            reserva_recurrente.fecha_inicio,
            reserva_recurrente.hora_inicio,
            reserva_recurrente.hora_fin,
            momento_actual
        )

        reservas = self.gestor.confirmar_reserva_recurrente(
            reserva_recurrente
        )

        self.notificar(
            reserva_recurrente.solicitante,
            reserva_recurrente.cancha,
            f"Reserva recurrente confirmada con {len(reservas)} semanas."
        )

        return reservas

    def cancelar(self, reserva, solicitante, momento_actual):
        estado = reserva.cancelar(solicitante, momento_actual)

        self.notificar(
            solicitante,
            reserva.cancha,
            f"Reserva {reserva.id} {estado.value}."
        )

        return estado

    def anular_reserva(self, reserva, administrador, momento_actual):
        if not isinstance(administrador, Administrador):
            raise PermissionError(
                "Solo un administrador puede anular una reserva."
            )

        if reserva.estado != EstadoReserva.CONFIRMADA:
            raise ValueError("La reserva ya no puede cambiar de estado.")

        estado = PoliticaAnulacionAdministrativa().cancelar(
            reserva,
            momento_actual
        )

        self.notificar(
            reserva.solicitante,
            reserva.cancha,
            f"Reserva {reserva.id} anulada administrativamente."
        )

        return estado

    def bloquear(self, administrador, plantilla, destinos):
        if not isinstance(administrador, Administrador):
            raise PermissionError(
                "Solo un administrador puede bloquear canchas."
            )

        bloques, reservas_afectadas = self.gestor.aplicar_bloqueo(
            plantilla,
            destinos
        )

        for reserva in reservas_afectadas:
            self.notificar(
                reserva.solicitante,
                reserva.cancha,
                f"Reserva {reserva.id} anulada por {plantilla.motivo}."
            )

        return bloques, reservas_afectadas