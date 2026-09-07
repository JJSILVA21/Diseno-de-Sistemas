from datetime import date, time

from dominio import Cancha, Estudiante, SolicitudReserva, Reserva, ConflictoAdministrativo

class GestorReservas:

    def __init__(self):
        self.canchas: list[Cancha] = []
        self.solicitudes: list[SolicitudReserva] = []
        self.reservas: list[Reserva] = []
        self.conflictos: list[ConflictoAdministrativo] = []
        self._contador_solicitudes = 1
        self._contador_reservas = 1

    def registrar_cancha(self, cancha: Cancha) -> None:
        for cancha_existente in self.canchas:
            if cancha_existente.id == cancha.id:
                raise ValueError("Ya existe una cancha con ese identificador.")
        self.canchas.append(cancha)

    def buscar_cancha(self,id_cancha: str) -> Cancha | None:
        for cancha in self.canchas:
            if cancha.id == id_cancha:
                return cancha
        return None

    def consultar_disponibilidad(self,solicitante: Estudiante,fecha: date,hora: time) -> list[Cancha]:
        if fecha < date.today():
            raise ValueError("No se pueden consultar fechas pasadas.")

        if not solicitante.puede_reservar(hora):
            return []

        disponibles = []

        for cancha in self.canchas:
            if cancha.esta_disponible(fecha,hora):
                disponibles.append(cancha)

        return disponibles

    def crear_solicitud(self,solicitante: Estudiante,cancha: Cancha,fecha: date,hora_inicio: time,momento_recepcion=None) -> SolicitudReserva:
        solicitud = SolicitudReserva(
            id_solicitud=f"SOL-{self._contador_solicitudes}",
            solicitante=solicitante,
            cancha=cancha,
            fecha=fecha,
            hora_inicio=hora_inicio,
            momento_recepcion=momento_recepcion
        )

        self._contador_solicitudes += 1
        self.solicitudes.append(solicitud)

        return solicitud

    def validar_solicitud(self,solicitud: SolicitudReserva) -> tuple[bool,str]:
        if solicitud.fecha < date.today():
            return False,"La fecha indicada es pasada."

        if solicitud.cancha not in self.canchas:
            return False,"La cancha no existe."

        if not solicitud.cancha.habilitada:
            return False,"La cancha está inhabilitada."

        if not solicitud.solicitante.puede_reservar(solicitud.hora_inicio):
            return False,"El estudiante regular solo puede reservar desde las 18:00."

        if not solicitud.cancha.esta_disponible(solicitud.fecha,solicitud.hora_inicio):
            return False,"La cancha ya no está disponible."

        return True,"Solicitud válida."

    def confirmar_reserva(self,solicitud: SolicitudReserva) -> Reserva:
        valida,mensaje = self.validar_solicitud(solicitud)

        if not valida:
            solicitud.rechazar()
            raise ValueError(mensaje)

        reserva = Reserva(id_reserva=f"RES-{self._contador_reservas}",estudiante=solicitud.solicitante,cancha=solicitud.cancha,fecha=solicitud.fecha,hora_inicio=solicitud.hora_inicio)
        self._contador_reservas += 1
        solicitud.aprobar()

        self.reservas.append(reserva)
        solicitud.solicitante.agregar_reserva(reserva)
        solicitud.cancha.agregar_reserva(reserva)

        return reserva

    def resolver_solicitudes_coincidentes(self,solicitudes: list[SolicitudReserva]) -> tuple[Reserva,SolicitudReserva,list[SolicitudReserva]]:
        if not solicitudes:
            raise ValueError("No existen solicitudes para resolver.")

        referencia = solicitudes[0]

        for solicitud in solicitudes[1:]:
            if not referencia.coincide_con(solicitud):
                raise ValueError("Las solicitudes no corresponden al mismo horario.")

        solicitudes_validas = []

        for solicitud in solicitudes:
            valida,_ = self.validar_solicitud(solicitud)

            if valida:
                solicitudes_validas.append(solicitud)
            else:
                solicitud.rechazar()

        if not solicitudes_validas:
            raise ValueError("Ninguna de las solicitudes es válida.")

        # Mayor nivel de prioridad gana.
        # Si tienen la misma prioridad, gana la solicitud recibida primero.
        solicitudes_ordenadas = sorted(
            solicitudes_validas,
            key=lambda solicitud: (
                -solicitud.solicitante.regla_prioridad.nivel_prioridad(),
                solicitud.momento_recepcion
            )
        )
        ganadora = solicitudes_ordenadas[0]
        perdedoras = [
            solicitud
            for solicitud in solicitudes
            if solicitud is not ganadora
        ]

        for solicitud in perdedoras:
            solicitud.rechazar()

        reserva = self.confirmar_reserva(ganadora)

        return reserva,ganadora,perdedoras

    def consultar_reservas_de(self,estudiante: Estudiante) -> list[Reserva]:
        return list(estudiante.reservas)

    def registrar_conflicto(self,conflicto: ConflictoAdministrativo) -> None:
        self.conflictos.append(conflicto)

    def consultar_conflictos(self) -> list[ConflictoAdministrativo]:
        return list(self.conflictos)