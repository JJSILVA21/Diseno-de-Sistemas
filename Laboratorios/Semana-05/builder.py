import copy

class Computadora: 
    def __init__(self):
        self.cpu = None
        self.ram = None
        self.disco = None
        self.gpu = None
        self.wifi = None
        
    def mostrar(self):
        print('CPU: ', self.cpu)
        print('RAM: ', self.ram)
        print('Disco: ', self.disco)
        print('GPU: ', self.gpu)
        print('Wi-Fi: ', self.wifi)

    def clonar(self):
          return copy.deepcopy(self)

class ComputadoraBuilder:
    def __init__(self):
            self.computadora = Computadora()

    def add_cpu(self, cpu):
            self.computadora.cpu = cpu
            return self

    def add_ram(self, ram):
            self.computadora.ram = ram
            return self

    def add_disco(self, disco):
            self.computadora.disco = disco
            return self

    def add_gpu(self, gpu):
            self.computadora.gpu = gpu
            return self

    def add_wifi(self, wifi:bool):
            self.computadora.wifi = wifi
            return self

    def build(self):
            return self.computadora

def main():
    pc_builder = ComputadoraBuilder()

    pc_builder = pc_builder.add_ram(4).add_gpu(18).add_wifi(True)

    pc_gaming = pc_builder.add_disco(1).add_cpu(20).build()

    pc_gaming.mostrar()

    print('\n Protipo: \n')

    pc_work = pc_gaming.clonar()

    pc_work.ram = 64

    pc_work.mostrar()


if __name__ == "__main__":
    main()