from config import GameConfig
from estrategias import AtaqueNormal, AtaqueFuerte
from factories import FantasyFactory, SciFiFactory


class GameFacade:

    def __init__(self):
        self.config = GameConfig.obtener_instancia()
        self.jugador = None
        self.enemigo = None

    def crear_mundo(self, mundo):

        mundo = mundo.lower()

        if mundo == "fantasia":
            factory = FantasyFactory()

        elif mundo == "scifi":
            factory = SciFiFactory()

        else:
            raise ValueError("Mundo no válido.")

        self.jugador = factory.crear_jugador()
        self.enemigo = factory.crear_enemigo()

        self.enemigo.cambiar_estrategia(AtaqueNormal())

        print(f"\nMundo creado: {mundo}")
        print(f"Jugador: {self.jugador.nombre}")
        print(f"Enemigo: {self.enemigo.nombre}")

    def seleccionar_estrategia(self, tipo_ataque):

        tipo_ataque = tipo_ataque.lower()

        if tipo_ataque == "normal":
            estrategia = AtaqueNormal()

        elif tipo_ataque == "fuerte":
            estrategia = AtaqueFuerte()

        else:
            raise ValueError("Estrategia no válida.")

        self.jugador.cambiar_estrategia(estrategia)

        print(
            f"{self.jugador.nombre} seleccionó "
            f"ataque {tipo_ataque}."
        )

    def ejecutar_turno(self):

        dano = self.jugador.atacar(self.enemigo)

        print(
            f"{self.jugador.nombre} ataca a "
            f"{self.enemigo.nombre} e inflige {dano} de daño."
        )

        if not self.enemigo.esta_vivo():
            return

        dano = self.enemigo.atacar(self.jugador)

        print(
            f"{self.enemigo.nombre} ataca a "
            f"{self.jugador.nombre} e inflige {dano} de daño."
        )

    def determinar_resultado(self):

        if self.jugador.esta_vivo() and not self.enemigo.esta_vivo():
            print(f"\nGanador: {self.jugador.nombre}")

        elif self.enemigo.esta_vivo() and not self.jugador.esta_vivo():
            print(f"\nGanador: {self.enemigo.nombre}")

        else:
            print("\nLa partida terminó sin ganador.")

    def jugar_partida(
        self,
        mundo,
        estrategia_inicial,
        estrategia_cambio,
        turno_cambio
    ):

        self.crear_mundo(mundo)

        print(f"Dificultad: {self.config.dificultad}")
        print(
            f"Máximo de turnos: "
            f"{self.config.numero_maximo_turnos}"
        )

        self.seleccionar_estrategia(estrategia_inicial)

        turno = 1

        while (
            self.jugador.esta_vivo()
            and self.enemigo.esta_vivo()
            and turno <= self.config.numero_maximo_turnos
        ):

            print(f"\n--- Turno {turno} ---")

            if turno == turno_cambio:
                self.seleccionar_estrategia(estrategia_cambio)

            self.ejecutar_turno()

            self.jugador.mostrar_estado()
            self.enemigo.mostrar_estado()

            turno += 1

        self.determinar_resultado()