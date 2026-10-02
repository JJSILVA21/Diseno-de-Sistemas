
class Personaje: 
    def __init__(self, nombre, vida, ataque): 
        self.nombre = nombre
        self.vida = vida
        self.ataque = ataque
        self.estrategia_ataque = None

    def cambiar_estrategia(self, estrategia):
        self.estrategia_ataque = estrategia

    def recibir_dano(self, dano):
        self.vida -= dano

        if self.vida < 0:
            self.vida = 0

    def atacar(self, enemigo):

        if self.estrategia_ataque is None:
            raise ValueError("El personaje no tiene una estrategia de ataque.")

        dano = self.estrategia_ataque.seleccionar(self.ataque)

        enemigo.recibir_dano(dano)

        return dano
    
    def esta_vivo(self):
            return self.vida > 0 
    
    def mostrar_estado(self):
        print(
            f"{self.nombre} | " 
            f"Vida:{self.vida} | " 
            f"Ataque: {self.ataque}"
        )

class Guerrero(Personaje):
    def __init__(self): 
        super().__init__( "Guerrero", 120, 20)

class Dragon(Personaje):
    def __init__(self): 
        super().__init__( "Dragón", 200, 50)

class Soldado(Personaje):
    def __init__(self): 
        super().__init__( "Soldado", 100, 15)

class Alien(Personaje):
    def __init__(self): 
        super().__init__( "Alien", 100, 25)



