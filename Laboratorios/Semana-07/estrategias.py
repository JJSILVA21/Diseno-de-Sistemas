from abc import ABC, abstractmethod

class EstrategiaAtaque(ABC):
    @abstractmethod
    def seleccionar(self, ataque_base):
        pass

class AtaqueNormal(EstrategiaAtaque):
    def seleccionar(self, ataque_base):
        return ataque_base 

class AtaqueFuerte(EstrategiaAtaque):
    def seleccionar(self, ataque_base):
        return ataque_base * 2
 
