class Recurso:
    def __init__(self, id_: int, puntos: int, columna: int = None, fila: int = None):
        self.id = id_
        self.puntos = puntos
        self.columna = columna
        self.fila = fila
        self.buscado= None

    def get_puntos(self) -> int:
        return self.puntos

    def set_posicion(self, columna: int, fila: int):
        self.columna = columna
        self.fila = fila


class Persona(Recurso):
    def __init__(self, id_: int, columna: int = None, fila: int = None):
        super().__init__(id_, 50, columna, fila)   # cada persona vale 50 puntos


class Ropa(Recurso):
    def __init__(self, id_: int, columna: int = None, fila: int = None):
        super().__init__(id_, 5, columna, fila)


class Alimentos(Recurso):
    def __init__(self, id_: int, columna: int = None, fila: int = None):
        super().__init__(id_, 10, columna, fila)


class Medicamentos(Recurso):
    def __init__(self, id_: int, columna: int = None, fila: int = None):
        super().__init__(id_, 20, columna, fila)


class Armamentos(Recurso):
    def __init__(self, id_: int, columna: int = None, fila: int = None):
        super().__init__(id_, 50, columna, fila)