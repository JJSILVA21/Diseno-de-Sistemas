
class GameConfig: 
    _instancia = None
    def __init__(self):
        self.dificultad = "Normal"
        self.numero_maximo_turnos = 10

    @staticmethod
    def obtener_instancia():
        if GameConfig._instancia is None:
            GameConfig._instancia = GameConfig()
        return GameConfig._instancia
    