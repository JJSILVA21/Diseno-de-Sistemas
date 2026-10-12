from datetime import date, datetime, time, timedelta
from threading import Barrier, Thread

from dominio import (
    Administrador,
    Bloqueo,
    Cancha,
    Capitan,
    Estudiante,
    ReservaRecurrenteBuilder,
    Sede,
)
from fachada import ReservaUFacade

def titulo(texto):
    print(f"\n{texto}")

def main():
    fachada = ReservaUFacade()

    norte = Sede("NORTE", "Campus Norte")
    sur = Sede("SUR", "Campus Sur")

    cancha_norte_1 = Cancha("N-01", "Cancha Norte 1", norte)
    cancha_norte_2 = Cancha("N-02", "Cancha Norte 2", norte)
    cancha_norte_3 = Cancha("N-03", "Cancha Norte 3", norte)
    cancha_sur_1 = Cancha("S-01", "Cancha Sur 1", sur)
    cancha_sur_2 = Cancha("S-02", "Cancha Sur 2", sur)
    for cancha in [
        cancha_norte_1,
        cancha_norte_2,
        cancha_norte_3,
        cancha_sur_1,
        cancha_sur_2,
    ]:
        fachada.registrar_cancha(cancha)
    estudiante = Estudiante("EST-001", "Juan", "juan@usfq.edu.ec")
    capitan = Capitan(
        "EST-002",
        "Carlos",
        "carlos@usfq.edu.ec",
        "Equipo Oficial USFQ"
    )
    administrador = Administrador("ADM-001", "Ana")
    fecha_base = date.today() + timedelta(days=10)

    titulo("1. RESERVAS EN CAMPUS NORTE Y CAMPUS SUR")

    reserva_norte = fachada.reservar(
        estudiante,
        cancha_norte_1,
        fecha_base,
        time(19, 0),
        time(20, 0)
    )
    reserva_sur = fachada.reservar(
        capitan,
        cancha_sur_1,
        fecha_base,
        time(8, 0),
        time(9, 0)
    )
    print(reserva_norte.id, reserva_norte.estado.value)
    print(reserva_sur.id, reserva_sur.estado.value)
    titulo("2. RECHAZO POR HORARIO DE LA SEDE")
    try:
        fachada.reservar(
            estudiante,
            cancha_sur_1,
            fecha_base,
            time(6, 0),
            time(7, 0)
        )
    except ValueError as error:
        print(error)

    titulo("3. RESERVA RECURRENTE")

    recurrente_exitosa = (
        ReservaRecurrenteBuilder(
            cancha_norte_2,
            fecha_base + timedelta(days=1),
            time(10, 0),
            time(11, 0),
            capitan
        )
        .con_numero_semanas(3)
        .con_equipo_prestado(["balones", "chalecos"])
        .con_notas("Entrenamiento oficial")
        .build()
    )

    reservas_recurrentes = fachada.reservar_recurrente(
        recurrente_exitosa
    )
    print("Semanas confirmadas:", len(reservas_recurrentes))

    fecha_conflicto = fecha_base + timedelta(days=2)

    fachada.reservar(
        capitan,
        cancha_norte_3,
        fecha_conflicto + timedelta(weeks=1),
        time(10, 0),
        time(11, 0)
    )
    recurrente_con_conflicto = (
        ReservaRecurrenteBuilder(
            cancha_norte_3,
            fecha_conflicto,
            time(10, 0),
            time(11, 0),
            capitan
        )
        .con_numero_semanas(3)
        .build()
    )
    try:
        fachada.reservar_recurrente(recurrente_con_conflicto)
    except ValueError as error:
        print(error)
        print("Reservas creadas:", len(recurrente_con_conflicto.reservas))

    titulo("4. CANCELACIONES")
    reserva_estudiante = fachada.reservar(
        estudiante,
        cancha_norte_1,
        fecha_base + timedelta(days=3),
        time(19, 0),
        time(20, 0)
    )

    estado_estudiante = fachada.cancelar(
        reserva_estudiante,
        estudiante,
        datetime.combine(
            fecha_base + timedelta(days=3),
            time(16, 0)
        )
    )

    print("Estudiante:", estado_estudiante.value)
    reserva_capitan = fachada.reservar(
        capitan,
        cancha_norte_1,
        fecha_base + timedelta(days=4),
        time(10, 0),
        time(11, 0)
    )

    estado_capitan = fachada.cancelar(
        reserva_capitan,
        capitan,
        datetime.combine(
            fecha_base + timedelta(days=4),
            time(9, 0)
        )
    )

    print("Capitán:", estado_capitan.value)
    reserva_administrativa = fachada.reservar(
        capitan,
        cancha_sur_1,
        fecha_base + timedelta(days=5),
        time(10, 0),
        time(11, 0)
    )

    estado_administrativo = fachada.anular_reserva(
        reserva_administrativa,
        administrador,
        datetime.combine(
            fecha_base + timedelta(days=5),
            time(8, 0)
        )
    )

    print("Administrador:", estado_administrativo.value)
    titulo("5. SUSPENSIÓN POR TRES NO-SHOWS")
    estudiante_suspendido = Estudiante(
        "EST-003",
        "María",
        "maria@usfq.edu.ec"
    )
    hoy = date.today()

    if hoy.month == 12:
        fecha_primer_no_show = date(hoy.year + 1, 1, 10)
    else:
        fecha_primer_no_show = date(hoy.year, hoy.month + 1, 10)
    fecha_ultimo_no_show = fecha_primer_no_show + timedelta(days=2)
    for indice in range(3):
        fecha_no_show = fecha_primer_no_show + timedelta(days=indice)

        reserva_no_show = fachada.reservar(
            estudiante_suspendido,
            cancha_norte_2,
            fecha_no_show,
            time(19, 0),
            time(20, 0)
        )
        fachada.cancelar(
            reserva_no_show,
            estudiante_suspendido,
            datetime.combine(fecha_no_show, time(18, 30))
        )
    print(
        "No-shows del mes:",
        estudiante_suspendido.contar_no_shows(
            datetime.combine(fecha_ultimo_no_show, time(18, 30))
        )
    )
    try:
        fachada.reservar(
            estudiante_suspendido,
            cancha_norte_2,
            fecha_ultimo_no_show + timedelta(days=1),
            time(19, 0),
            time(20, 0),
            datetime.combine(fecha_ultimo_no_show, time(18, 31))
        )
    except ValueError as error:
        print(error)

    titulo("6. BLOQUEO CLONADO")

    fecha_bloqueo = fecha_base + timedelta(days=30)

    reserva_afectada = fachada.reservar(
        capitan,
        cancha_norte_3,
        fecha_bloqueo,
        time(13, 0),
        time(14, 0)
    )

    plantilla = Bloqueo(
        "BLOQ-001",
        "Mantenimiento",
        time(13, 0),
        time(14, 0),
        ["red"]
    )

    bloqueos, reservas_afectadas = fachada.bloquear(
        administrador,
        plantilla,
        [
            (cancha_norte_3, fecha_bloqueo),
            (cancha_sur_2, fecha_bloqueo),
        ]
    )

    bloqueos[0].equipo.append("balones")
    print("Bloqueos creados:", len(bloqueos))
    print("Reservas anuladas:", len(reservas_afectadas))
    print("Estado afectado:", reserva_afectada.estado.value)
    print("Equipo de plantilla:", plantilla.equipo)
    titulo("7. DOS SOLICITUDES SIMULTÁNEAS")
    estudiante_1 = Estudiante("EST-004", "Pedro", "pedro@usfq.edu.ec")
    estudiante_2 = Estudiante("EST-005", "Lucía", "lucia@usfq.edu.ec")
    barrera = Barrier(2)
    resultados = []
    fecha_concurrente = fecha_base + timedelta(days=40)

    def intentar_reserva(solicitante):
        barrera.wait()

        try:
            reserva = fachada.reservar(
                solicitante,
                cancha_sur_2,
                fecha_concurrente,
                time(19, 0),
                time(20, 0)
            )
            resultados.append(
                f"{solicitante.nombre}: confirmada {reserva.id}"
            )
        except ValueError:
            resultados.append(f"{solicitante.nombre}: rechazada")

    hilo_1 = Thread(
        target=intentar_reserva,
        args=(estudiante_1,)
    )

    hilo_2 = Thread(
        target=intentar_reserva,
        args=(estudiante_2,)
    )

    hilo_1.start()
    hilo_2.start()
    hilo_1.join()
    hilo_2.join()

    for resultado in resultados:
        print(resultado)

    print(
        "Confirmadas:",
        sum("confirmada" in resultado for resultado in resultados)
    )

if __name__ == "__main__":
    main()