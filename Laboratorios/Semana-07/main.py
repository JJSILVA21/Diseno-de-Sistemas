from config import GameConfig
from game_facade import GameFacade


def main():

    config = GameConfig.obtener_instancia()

    config.dificultad = "Normal"
    config.numero_maximo_turnos = 10

    juego = GameFacade()

    juego.jugar_partida(
        "scifi",
        "normal",
        "fuerte",
        2
    )


if __name__ == "__main__":
    main()