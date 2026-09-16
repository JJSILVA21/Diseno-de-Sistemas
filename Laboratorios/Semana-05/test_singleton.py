from singleton import GestorDeConfiguracion, reserva_permitida


def test_rechaza_reserva_durante_mantenimiento():
    config = GestorDeConfiguracion.obtener_objeto()
    config.modo_mantenimiento = True

    assert reserva_permitida(config) is False


def test_acepta_reserva_fuera_de_mantenimiento():
    config = GestorDeConfiguracion.obtener_objeto()

    # El Singleton conserva el estado establecido por otras partes del programa.
    # Por eso el test debe declarar explícitamente el estado que necesita.
    config.modo_mantenimiento = False

    assert reserva_permitida(config) is True


def test_obtener_objeto_reutiliza_la_misma_instancia():
    primera_referencia = GestorDeConfiguracion.obtener_objeto()
    segunda_referencia = GestorDeConfiguracion.obtener_objeto()

    assert primera_referencia is segunda_referencia
