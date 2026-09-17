from singleton import GestorDeConfiguracion, reserva_permitida


class Estudiante:

    def __init__(self, nombre: str):
        self.nombre = nombre


class EquipoOficial:

    def __init__(self, nombre: str):
        self.nombre = nombre


class ReservaRegular:

    def __init__(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.solicitante = solicitante
        self.tipo = "Regular"
    def confirmar(self): 
            return "Reserva confirmada para " + self.solicitante.nombre

class ReservaPrioridad:

    def __init__(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        self.cancha = cancha
        self.fecha = fecha
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.solicitante = solicitante
        self.tipo = "Prioridad"
    def confirmar(self): 
        return "Reserva con prioridad confirmada para " + self.solicitante.nombre
    
def reservar_desde_web(cancha, fecha, hora_inicio, hora_fin, solicitante):
    creador = FabricaDeReservas.elegir_creador(solicitante)
    reserva = creador.crear_reserva(
        cancha,
        fecha,
        hora_inicio,
        hora_fin,
        solicitante
        )

    return reserva
    


def reservar_desde_hall(cancha, fecha, hora_inicio, hora_fin, equipo):

    gestor = GestorDeConfiguracion.obtener_objeto()

    if not reserva_permitida(gestor):
        return "No se puede realizar la reserva: el sistema está en mantenimiento."

    reserva = ReservaPrioridad(
        cancha,
        fecha,
        hora_inicio,
        hora_fin,
        equipo
    )

    return reserva

class CreadorDeReserva():
    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        raise NotImplementedError
    
class CreadorDeReservaRegular(CreadorDeReserva):
    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        return ReservaRegular(
            cancha,
            fecha,
            hora_inicio,
            hora_fin,
            solicitante
        )

class CreadorDeReservaPrioritaria(CreadorDeReserva):
    def crear_reserva(self, cancha, fecha, hora_inicio, hora_fin, solicitante):
        return ReservaPrioridad(
            cancha,
            fecha,
            hora_inicio,
            hora_fin,
            solicitante
        )

class FabricaDeReservas():
    @staticmethod
    def elegir_creador(solicitante):
        if isinstance(solicitante, Estudiante):
            return CreadorDeReservaRegular()
        elif isinstance(solicitante, EquipoOficial):
            return CreadorDeReservaPrioritaria()

        
def main():

    reserva_1 = reservar_desde_web(
        "Cancha de fútbol",
        "2026-09-17",
        "20:00",
        "21:00",
        Estudiante("Erick")
    )

    print(reserva_1.confirmar())

    reserva_2 = reservar_desde_web(
        "Cancha de fútbol",
        "2026-09-17",
        "20:00",
        "21:00",
        EquipoOficial("Erick capitán")
    )
    print(reserva_2.confirmar())

if __name__ == "__main__":
    main()