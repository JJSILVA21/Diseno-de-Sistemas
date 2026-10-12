from datetime import time

class ConfiguracionReservaU:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            instancia = super().__new__(cls)
            instancia.hora_prioridad = time(18, 0)
            instancia.cancelacion_estudiante_horas = 2
            instancia.cancelacion_capitan_horas = 24
            instancia.limite_no_shows = 3
            instancia.dias_suspension = 7
            cls._instancia = instancia
        return cls._instancia

    @classmethod
    def obtener_instancia(cls):
        return cls()