# Tenemos un vehiculo y este vehiculo debe moverse. La funcion se va a llamar mover. Pero hay diferentes tipos de vehiculo:
# Auto -> se mueve por carretera
# Bote -> se mueve por agua
# Avion -> se mueve por aire

# Necesitamos hacer que el vehiculo se mueva, pero no sabemos que tipo de vehiculo es. Por lo tanto, necesitamos una clase abstracta que defina el comportamiento de mover. Es decir, hacer composicion.

class ComportamientoMover:
    def mover(self):
        raise NotImplementedError
    
class MoverPorCarretera(ComportamientoMover):
    def mover(self):
        print("Conduciendo por carretera")
        
class MoverPorAgua(ComportamientoMover):
    def mover(self):
        print("Navegando por agua")

class MoverPorAire(ComportamientoMover):
    def mover(self):
        print("Volando por el aire")

class Vehiculo:
    def __init__(self, comportamiento_mover):
        self.comportamiento_mover = comportamiento_mover

    def mover(self): 
        self.comportamiento_mover.mover()

class Auto(Vehiculo):
    def __init__(self): 
        mover_carretera = MoverPorCarretera()
        super().__init__(mover_carretera)
        
class Bote(Vehiculo):
    def __init__(self):
        mover_agua = MoverPorAgua()
        super().__init__(mover_agua)

class Avion(Vehiculo):
    def __init__(self):
        mover_aire = MoverPorAire()
        super().__init__(mover_aire)

if __name__ == "__main__":
    auto = Auto()
    auto.mover()

    bote = Bote()
    bote.mover()

    avion = Avion()
    avion.mover()
