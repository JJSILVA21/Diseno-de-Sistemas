from abc import ABC, abstractmethod
from datetime import time

from dominio import (
    Capitan,
    PoliticaCancelacionCapitan,
    PoliticaCancelacionEstudiante,
    ReservaEquipoOficial,
    ReservaRegular,
)

class CreadorReserva(ABC):
    @abstractmethod
    def crear_reserva(
        self,
        id_reserva,
        solicitante,
        cancha,
        fecha,
        hora_inicio,
        hora_fin
    ):
        pass

class CreadorReservaRegular(CreadorReserva):
    def crear_reserva(
        self,
        id_reserva,
        solicitante,
        cancha,
        fecha,
        hora_inicio,
        hora_fin
    ):
        return ReservaRegular(
            id_reserva,
            solicitante,
            cancha,
            fecha,
            hora_inicio,
            hora_fin,
            PoliticaCancelacionEstudiante()
        )

class CreadorReservaEquipo(CreadorReserva):
    def crear_reserva(
        self,
        id_reserva,
        solicitante,
        cancha,
        fecha,
        hora_inicio,
        hora_fin
    ):
        return ReservaEquipoOficial(
            id_reserva,
            solicitante,
            cancha,
            fecha,
            hora_inicio,
            hora_fin,
            PoliticaCancelacionCapitan()
        )

class FabricaReservas:
    @staticmethod
    def elegir_creador(solicitante):
        if isinstance(solicitante, Capitan):
            return CreadorReservaEquipo()

        return CreadorReservaRegular()

class ValidadorHorario(ABC):
    @abstractmethod
    def esta_permitido(self, hora_inicio, hora_fin):
        pass

class ValidadorHorarioNorte(ValidadorHorario):
    def esta_permitido(self, hora_inicio, hora_fin):
        return time(6, 0) <= hora_inicio < hora_fin <= time(22, 0)

class ValidadorHorarioSur(ValidadorHorario):
    def esta_permitido(self, hora_inicio, hora_fin):
        return time(7, 0) <= hora_inicio < hora_fin <= time(23, 0)

class Notificador(ABC):
    @abstractmethod
    def notificar(self, solicitante, mensaje):
        pass

class NotificadorCorreo(Notificador):
    def notificar(self, solicitante, mensaje):
        print(f"Correo a {solicitante.correo}: {mensaje}")


class NotificadorSMS(Notificador):
    def notificar(self, solicitante, mensaje):
        print(f"SMS a {solicitante.nombre}: {mensaje}")

class FabricaSede(ABC):
    @abstractmethod
    def crear_validador_horario(self):
        pass

    @abstractmethod
    def crear_notificador(self):
        pass

class FabricaSedeNorte(FabricaSede):
    def crear_validador_horario(self):
        return ValidadorHorarioNorte()

    def crear_notificador(self):
        return NotificadorCorreo()

class FabricaSedeSur(FabricaSede):
    def crear_validador_horario(self):
        return ValidadorHorarioSur()

    def crear_notificador(self):
        return NotificadorSMS()

class FabricaSedes:
    @staticmethod
    def obtener(sede):
        if sede.id == "NORTE":
            return FabricaSedeNorte()

        if sede.id == "SUR":
            return FabricaSedeSur()

        raise ValueError("La sede no está configurada.")