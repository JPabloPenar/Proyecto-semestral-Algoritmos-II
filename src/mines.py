class Mina:
    def __init__(self, id_: int, tipo: str, columna: int = None, fila: int = None,
                 radio: float = 0, direccion: str = None, movil: bool = False):
        self.id = id_
        self.tipo = tipo
        self.columna = columna
        self.fila = fila
        self.radio = radio          # en minas circulares, radio de efecto
        self.direccion = direccion  # "horizontal" o "vertical" en minas lineales
        self.movil = movil          # True si aparece/desaparece (solo G1)

    def set_posicion(self, columna: int, fila: int):
        self.columna = columna
        self.fila = fila


class MinaO1(Mina):
    def __init__(self, id_: int, columna: int = None, fila: int = None):
        super().__init__(id_, "O1", columna, fila, radio=10, movil=False)


class MinaO2(Mina):
    def __init__(self, id_: int, columna: int = None, fila: int = None):
        super().__init__(id_, "O2", columna, fila, radio=5, movil=False)


class MinaT1(Mina):
    def __init__(self, id_: int, columna: int = None, fila: int = None):
        super().__init__(id_, "T1", columna, fila, radio=10, direccion="horizontal", movil=False)


class MinaT2(Mina):
    def __init__(self, id_: int, columna: int = None, fila: int = None):
        super().__init__(id_, "T2", columna, fila, radio=5, direccion="vertical", movil=False)


class MinaG1(Mina):
    def __init__(self, id_: int, columna: int = None, fila: int = None):
        super().__init__(id_, "G1", columna, fila, radio=7, movil=True)
