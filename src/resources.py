# Clase base para los recursos y clases derivadas para cada tipo de recurso

class Recurso:
    def __init__(self, id_: int, puntos: int, x: float = None, y: float = None):
        self.id = id_
        self.puntos = puntos
        self.x = x
        self.y = y

    def get_puntos(self) -> int:
        return self.puntos

    def set_posicion(self, x: float, y: float):
        self.x = x
        self.y = y


class Persona(Recurso):
    def __init__(self, id_: int, x: float = None, y: float = None):
        super().__init__(id_, 50, x, y)   # cada persona vale 50 puntos


class Ropa(Recurso):
    def __init__(self, id_: int, x: float = None, y: float = None):
        super().__init__(id_, 5, x, y)


class Alimentos(Recurso):
    def __init__(self, id_: int, x: float = None, y: float = None):
        super().__init__(id_, 10, x, y)


class Medicamentos(Recurso):
    def __init__(self, id_: int, x: float = None, y: float = None):
        super().__init__(id_, 20, x, y)


class Armamentos(Recurso):
    def __init__(self, id_: int, x: float = None, y: float = None):
        super().__init__(id_, 50, x, y)
