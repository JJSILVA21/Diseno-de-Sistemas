class GestorDeConfiguracion:
    _objeto = None

    def __init__(self):
        self.modo_mantenimiento = False

    @staticmethod
    def obtener_objeto():
        if GestorDeConfiguracion._objeto is None:
            GestorDeConfiguracion._objeto = GestorDeConfiguracion()

        return GestorDeConfiguracion._objeto


def reserva_permitida(gestor):
    return not gestor.modo_mantenimiento