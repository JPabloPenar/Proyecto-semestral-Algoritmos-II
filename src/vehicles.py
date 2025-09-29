class vehicle:
    def __init__(self, canvas, posicionX, posicionY, tipoDeCarga, viajes, tag, equipo):
        self.canvas = canvas              # Referencia al canvas de Tkinter
        self.posicionX = posicionX
        self.posicionY = posicionY
        self.carga = tipoDeCarga
        self.viajes = viajes
        self.tag = tag  
        self.equipo = equipo

    def explotar(self):
        pass 
    
    def recoger(self):
        self.viajes -= 1
    
    # Movimiento
    def irArriba(self):
        self.posicionY -= 5
        self.mover_en_canvas(0, -5)

    def irAbajo(self):
        self.posicionY += 5
        self.mover_en_canvas(0, 5)

    def irDerecha(self):
        self.posicionX += 5
        self.mover_en_canvas(5, 0)

    def irIzquierda(self):
        self.posicionX -= 5
        self.mover_en_canvas(-5, 0)
    
    def mover_en_canvas(self, dx, dy):
        self.canvas.move(self.tag, dx, dy)


# ----- Subclases -----

class jeep(vehicle):
    def __init__(self, canvas, posicionX, posicionY, tag, equipo):
        super().__init__(canvas, posicionX, posicionY, "todo", 2, tag, equipo)

class moto(vehicle):
    def __init__(self, canvas, posicionX, posicionY, tag, equipo):
        super().__init__(canvas, posicionX, posicionY, "personas", 1, tag, equipo)

class auto(vehicle):
    def __init__(self, canvas, posicionX, posicionY, tag, equipo):
        super().__init__(canvas, posicionX, posicionY, "todo", 1, tag, equipo)

class camion(vehicle):
    def __init__(self, canvas, posicionX, posicionY, tag, equipo):
        super().__init__(canvas, posicionX, posicionY, "todo", 3, tag, equipo)
