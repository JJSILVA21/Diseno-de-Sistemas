from datetime import timedelta
from threading import Lock

from dominio import (
    Bloqueo,
    EstadoReserva,
    PoliticaAnulacionAdministrativa,
)
from fabricas import FabricaReservas


class GestorReservas:
    def __init__(self):
        self.canchas = []
        self.reservas = []
        self.bloqueos = []
        self.contador_reservas = 1
        self.lock = Lock()

    def registrar_cancha(self, cancha):
        if any(cancha_existente.id == cancha.id for cancha_existente in self.canchas):
            raise ValueError("Ya existe una cancha con ese identificador.")

        self.canchas.append(cancha)

    def consultar_reservas_de(self, solicitante):
        return list(solicitante.reservas)

    def se_superponen(self, inicio_a, fin_a, inicio_b, fin_b):
        return inicio_a < fin_b and inicio_b < fin_a

    def esta_disponible(self, cancha, fecha, hora_inicio, hora_fin):
        for reserva in self.reservas:
            if (
                reserva.cancha is cancha
                and reserva.fecha == fecha
                and reserva.estado == EstadoReserva.CONFIRMADA
                and self.se_superponen(
                    hora_inicio,
                    hora_fin,
                    reserva.hora_inicio,
                    reserva.hora_fin
                )
            ):
                return False

        for bloqueo in self.bloqueos:
            if (
                bloqueo.cancha is cancha
                and bloqueo.fecha == fecha
                and self.se_superponen(
                    hora_inicio,
                    hora_fin,
                    bloqueo.hora_inicio,
                    bloqueo.hora_fin
                )
            ):
                return False

        return cancha.habilitada

    def crear_reserva(
        self,
        solicitante,
        cancha,
        fecha,
        hora_inicio,
        hora_fin
    ):
        creador = FabricaReservas.elegir_creador(solicitante)

        reserva = creador.crear_reserva(
            f"RES-{self.contador_reservas}",
            solicitante,
            cancha,
            fecha,
            hora_inicio,
            hora_fin
        )

        self.contador_reservas += 1
        self.reservas.append(reserva)
        solicitante.agregar_reserva(reserva)

        return reserva

    def confirmar_reserva(
        self,
        solicitante,
        cancha,
        fecha,
        hora_inicio,
        hora_fin
    ):
        with self.lock:
            if not self.esta_disponible(
                cancha,
                fecha,
                hora_inicio,
                hora_fin
            ):
                raise ValueError("La cancha no está disponible.")

            return self.crear_reserva(
                solicitante,
                cancha,
                fecha,
                hora_inicio,
                hora_fin
            )

    def confirmar_reserva_recurrente(self, reserva_recurrente):
        with self.lock:
            fechas = [
                reserva_recurrente.fecha_inicio + timedelta(weeks=semana)
                for semana in range(reserva_recurrente.numero_semanas)
            ]

            for indice, fecha in enumerate(fechas, start=1):
                if not self.esta_disponible(
                    reserva_recurrente.cancha,
                    fecha,
                    reserva_recurrente.hora_inicio,
                    reserva_recurrente.hora_fin
                ):
                    raise ValueError(
                        f"La semana {indice} tiene un conflicto. No se creó ninguna reserva."
                    )

            reservas = []

            for fecha in fechas:
                reserva = self.crear_reserva(
                    reserva_recurrente.solicitante,
                    reserva_recurrente.cancha,
                    fecha,
                    reserva_recurrente.hora_inicio,
                    reserva_recurrente.hora_fin
                )
                reservas.append(reserva)

            reserva_recurrente.reservas = reservas

            return reservas

    def aplicar_bloqueo(self, plantilla, destinos):
        with self.lock:
            bloques = []
            reservas_afectadas = []
            politica = PoliticaAnulacionAdministrativa()

            for cancha, fecha in destinos:
                clon = plantilla.clonar(cancha, fecha)
                bloques.append(clon)

                for reserva in self.reservas:
                    if (
                        reserva.cancha is cancha
                        and reserva.fecha == fecha
                        and reserva.estado == EstadoReserva.CONFIRMADA
                        and self.se_superponen(
                            clon.hora_inicio,
                            clon.hora_fin,
                            reserva.hora_inicio,
                            reserva.hora_fin
                        )
                    ):
                        politica.cancelar(
                            reserva,
                            reserva.fecha_hora_inicio()
                        )
                        reservas_afectadas.append(reserva)

            self.bloqueos.extend(bloques)

            return bloques, reservas_afectadas