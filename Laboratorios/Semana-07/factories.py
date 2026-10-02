from abc import ABC, abstractmethod
from personajes import Personaje, Guerrero, Dragon, Soldado, Alien

class PersonajeFactory(ABC):
    @staticmethod
    def crear(tipo):
        tipo = tipo.lower()
        if tipo == "guerrero":
            return Guerrero()
        elif tipo == "dragon":
            return Dragon()
        elif tipo == "soldado":
            return Soldado()
        elif tipo == "alien":
            return Alien()
        else: 
            raise ValueError(f"Tipo de personaje desconocido: {tipo}")
        

#--------------------------------------------------------------------------------------------
# Abstract Factory
#--------------------------------------------------------------------------------------------

class MundoFactory(ABC):

    @abstractmethod
    def crear_jugador(self):
        pass

    @abstractmethod
    def crear_enemigo(self):
        pass

#--------------------------------------------------------------------------------------------
# Factories
#--------------------------------------------------------------------------------------------

class FantasyFactory(MundoFactory):
    def crear_jugador(self):
        return Guerrero()

    def crear_enemigo(self):
        return Dragon()

class SciFiFactory(MundoFactory):
    def crear_jugador(self):
        return Soldado()

    def crear_enemigo(self):
        return Alien()