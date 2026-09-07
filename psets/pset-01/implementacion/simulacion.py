from datetime import date, datetime, time, timedelta

from dominio import Administrador, Cancha, Capitan, ConflictoAdministrativo, CuentaInstitucional, Estudiante, SinPrioridad
from gestor_reservas import GestorReservas

def titulo(texto):
    print("\n")
    print(texto)


def mostrar_canchas(canchas):
    if not canchas:
        print("No existen canchas disponibles.")
        return

    for cancha in canchas:
        print(f"- {cancha}")

def main():

    titulo("INICIO DE SIMULACION DE RESERVAU")

    gestor = GestorReservas()

    estudiante = Estudiante("EST-001","Juan",SinPrioridad())

    capitan = Capitan("EST-002","Carlos","Equipo Oficial USFQ")

    administrador = Administrador( "ADM-001","Administrador ReservaU")

    cuenta_estudiante = CuentaInstitucional("juan@estud.usfq.edu.ec","1234",estudiante
    )

    cuenta_capitan = CuentaInstitucional("carlos@estud.usfq.edu.ec","5678",capitan)

    cancha_1 = Cancha("C01","Cancha de futbol")

    cancha_2 = Cancha("C02","Cancha de basquet")

    gestor.registrar_cancha(cancha_1)
    gestor.registrar_cancha(cancha_2)

    fecha_reserva = date.today() + timedelta(days=2)

    titulo("PRECONDICIONES")

    print("Autenticacion estudiante:",cuenta_estudiante.autenticar("1234"))
    print("Autenticacion capitan:",cuenta_capitan.autenticar("5678"))
    print("Tipo de solicitante 1:",type(cuenta_estudiante.obtener_propietario()).__name__)
    print("Tipo de solicitante 2:",type(cuenta_capitan.obtener_propietario()).__name__)

    titulo("1. CASO DE USO: CONSULTAR CANCHAS DISPONIBLES")

    hora_consulta = time(19,0)

    print(f"Estudiante consulta disponibilidad para {fecha_reserva} a las {hora_consulta.strftime('%H:%M')}.")

    disponibles = gestor.consultar_disponibilidad(
        estudiante,
        fecha_reserva,
        hora_consulta
    )

    print("Canchas disponibles:")
    mostrar_canchas(disponibles)

    print("\nFlujo alterno: consulta de fecha pasada.")

    try:
        gestor.consultar_disponibilidad(
            estudiante,
            date.today() - timedelta(days=1),
            hora_consulta
        )
    except ValueError as error:
        print(error)

    titulo("2. CASO DE USO: REALIZAR RESERVA")

    solicitud = gestor.crear_solicitud(estudiante,cancha_1,fecha_reserva,time(19,0))

    reserva = gestor.confirmar_reserva(solicitud)

    print("Reserva creada correctamente.")
    print(reserva)

    print("\nFlujo alterno: estudiante regular intenta reservar antes de las 18:00.")

    solicitud_temprana = gestor.crear_solicitud(estudiante,cancha_2,fecha_reserva,time(16,0))

    try:
        gestor.confirmar_reserva(solicitud_temprana)
    except ValueError as error:
        print("Solicitud rechazada:",error)

    print("\nCapitan intenta reservar antes de las 18:00.")

    solicitud_capitan_temprana = gestor.crear_solicitud(capitan,cancha_2,fecha_reserva,time(16,0))

    reserva_capitan_temprana = gestor.confirmar_reserva(solicitud_capitan_temprana)

    print("Reserva del capitan confirmada.")
    print(reserva_capitan_temprana)

    print("\nFlujo alterno: solicitudes coincidentes.")

    fecha_colision = date.today() + timedelta(days=5)

    momento_1 = datetime.now()
    momento_2 = momento_1 + timedelta(seconds=1)

    solicitud_estudiante = gestor.crear_solicitud(estudiante,cancha_1,fecha_colision,time(19,0),momento_1)

    solicitud_capitan = gestor.crear_solicitud(capitan,cancha_1,fecha_colision,time(19,0),momento_2)

    reserva_colision,ganadora,perdedoras = gestor.resolver_solicitudes_coincidentes(
        [
            solicitud_estudiante,
            solicitud_capitan
        ]
    )

    print("Ganador de la solicitud coincidente:",ganadora.solicitante.nombre)
    print("Tipo:",type(ganadora.solicitante).__name__)

    for perdedora in perdedoras:
        print(
            f"Solicitud de {perdedora.solicitante.nombre}: "
            f"{perdedora.estado.value}"
        )

    print("\nFlujo alterno: dos estudiantes del mismo tipo.")

    estudiante_2 = Estudiante(
        "EST-003",
        "Ana",
        SinPrioridad()
    )

    fecha_colision_2 = date.today() + timedelta(days=6)

    momento_a = datetime.now()
    momento_b = momento_a + timedelta(seconds=2)

    solicitud_primera = gestor.crear_solicitud(estudiante,cancha_2,fecha_colision_2,time(20,0),momento_a)

    solicitud_segunda = gestor.crear_solicitud(estudiante_2,cancha_2,fecha_colision_2,time(20,0),momento_b)

    _,ganadora_mismo_tipo,_ = gestor.resolver_solicitudes_coincidentes(
        [
            solicitud_primera,
            solicitud_segunda
        ]
    )

    print("Ganador entre estudiantes del mismo tipo:",ganadora_mismo_tipo.solicitante.nombre)
    print("Se selecciono la solicitud recibida primero.")

    titulo("3. CASO DE USO: CONSULTAR RESERVAS PROPIAS")

    reservas_estudiante = gestor.consultar_reservas_de(estudiante)

    print(f"Reservas de {estudiante.nombre}:")

    for reserva_estudiante in reservas_estudiante:
        print(reserva_estudiante)

    titulo("4. CASO DE USO: CANCELAR RESERVA PROPIA")

    fecha_cancelacion = date.today() + timedelta(days=10)

    solicitud_cancelacion = gestor.crear_solicitud(estudiante,cancha_1,fecha_cancelacion,time(19,0))

    reserva_cancelacion = gestor.confirmar_reserva(solicitud_cancelacion)

    momento_actual = datetime.combine(
        fecha_cancelacion,
        time(15,0)
    )

    estado = reserva_cancelacion.cancelar(
        estudiante,
        momento_actual
    )

    print("Cancelacion realizada con mas de dos horas de anticipacion.")
    print("Estado:",estado.value)

    print("\nFlujo alterno: cancelacion con menos de dos horas.")

    fecha_no_show = date.today() + timedelta(days=11)

    solicitud_no_show = gestor.crear_solicitud(estudiante,cancha_1,fecha_no_show,time(19,0))

    reserva_no_show = gestor.confirmar_reserva(solicitud_no_show)

    momento_tardio = datetime.combine(
        fecha_no_show,
        time(17,30)
    )

    estado_tardio = reserva_no_show.cancelar(
        estudiante,
        momento_tardio
    )

    print("Estado de cancelacion tardia:",estado_tardio.value)

    print("\nFlujo alterno: intentar cancelar una reserva ajena.")

    try:
        reserva_capitan_temprana.cancelar(
            estudiante,
            datetime.now()
        )
    except PermissionError as error:
        print(error)

    titulo("5. CASO DE USO: REGISTRAR CANCHA")

    nueva_cancha = Cancha(
        "C03",
        "Cancha de voley"
    )

    administrador.registrar_cancha(
        gestor,
        nueva_cancha
    )

    print("Administrador registro:",nueva_cancha)

    titulo("6. CASO DE USO: HABILITAR CANCHA")

    nueva_cancha.inhabilitar()

    print("Estado antes:",nueva_cancha)

    administrador.habilitar_cancha(nueva_cancha)

    print("Estado despues:",nueva_cancha)

    titulo("7. CASO DE USO: INHABILITAR CANCHA")

    administrador.inhabilitar_cancha(nueva_cancha)

    print("Cancha inhabilitada:",nueva_cancha)

    titulo("8. CASO DE USO: CONSULTAR CONFLICTOS ADMINISTRATIVOS")

    conflicto = ConflictoAdministrativo(
        "CONF-001",
        "Reclamo relacionado con una reserva.",
        [reserva_colision]
    )

    gestor.registrar_conflicto(conflicto)

    conflictos = administrador.consultar_conflictos(
        gestor.consultar_conflictos()
    )

    if conflictos:
        for conflicto_actual in conflictos:
            print(conflicto_actual)
    else:
        print("No existen conflictos administrativos.")

    titulo("9. CASO DE USO: INTERVENIR EN CONFLICTO ADMINISTRATIVO")

    print("Estado antes de la intervencion:",conflicto.estado.value)

    administrador.intervenir_conflicto(conflicto)

    print("Estado despues de la intervencion:",conflicto.estado.value)

    for intervencion in conflicto.intervenciones:
        print(intervencion)

    titulo("SIMULACION FINALIZADA CORRECTAMENTE")
if __name__ == "__main__":
    main()