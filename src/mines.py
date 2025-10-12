# Clase base para las minas y clases derivadas para cada tipo de mina

class Mina:
    def __init__(self, id_: int, tipo: str, x: float = None, y: float = None,
                 radio: float = 0, direccion: str = None, movil: bool = False):
        self.id = id_
        self.tipo = tipo
        self.x = x
        self.y = y
        self.radio = radio          # en minas circulares, radio de efecto
        self.direccion = direccion  # "horizontal" o "vertical" en minas lineales
        self.movil = movil          # True si aparece/desaparece (solo G1)

    def set_posicion(self, x: float, y: float):
        self.x = x
        self.y = y


class MinaO1(Mina):
    def __init__(self, id_: int, x: float = None, y: float = None):
        super().__init__(id_, "O1", x, y, radio=10, movil=False)


class MinaO2(Mina):
    def __init__(self, id_: int, x: float = None, y: float = None):
        super().__init__(id_, "O2", x, y, radio=5, movil=False)


class MinaT1(Mina):
    def __init__(self, id_: int, x: float = None, y: float = None):
        super().__init__(id_, "T1", x, y, radio=10, direccion="horizontal", movil=False)


class MinaT2(Mina):
    def __init__(self, id_: int, x: float = None, y: float = None):
        super().__init__(id_, "T2", x, y, radio=5, direccion="vertical", movil=False)


class MinaG1(Mina):
    def __init__(self, id_: int, x: float = None, y: float = None):
        super().__init__(id_, "G1", x, y, radio=7, movil=True)
