class vehicle:    
    def __init__(self, posicionX, posicionY, viajesTotales, viajesActuales, tipoDeCarga, equipo, estado): 
        #los viajes totales también son la capacacidad

        self.posicionX = posicionX
        self.posicionY = posicionY
        self.carga = tipoDeCarga
        self.viajesTotales = viajesTotales
        self.viajesActuales = viajesActuales
        self.equipo = equipo
        self.estado = estado

    def explotar(self):
        self.estado = "explotado"

    def recoger(self):
            self.viajesActuales -= 1 
            if self.viajesActuales == 0: #si tiene la carga 
                #volver a base para descargar
                pass

    def descargar(self): # Se completa un viaje y se reestablecen la cantidad de viajes y se le suman los puntos al equipo
        
        self.viajesActuales=self.viajesTotales
        

    # Movimiento
    def irArriba(self):
        self.posicionY -= 5
      

    def irAbajo(self):
        self.posicionY += 5
        

    def irDerecha(self):
        self.posicionX += 5
       

    def irIzquierda(self):
        self.posicionX -= 5
        
    
    # def mover_en_canvas(self, dx, dy):


# ----- Subclases -----
# Cada subclase define sus atributos de capacidad y carga explícitamente.
#(self, posicionX, posicionY, viajesTotales, viajesActuales, tipoDeCarga, equipo, estado)
class jeep(vehicle):
    def __init__(self, posicionX, posicionY, viajesTotales, viajesActuales, tipoDeCarga, equipo, estado):
        super().__init__(posicionX, posicionY, 2, 2, "todo", equipo, "activo")

class moto(vehicle):
    def __init__(self, posicionX, posicionY, viajesTotales, viajesActuales, tipoDeCarga, equipo, estado):
        super().__init__(posicionX, posicionY, 1, 1, "personas", equipo, "activo")

class auto(vehicle):
    def __init__(self, posicionX, posicionY, viajesTotales, viajesActuales, tipoDeCarga, equipo, estado):
        super().__init__(posicionX, posicionY, 1, 1, "todo", equipo, "activo")

class camion(vehicle):
    def __init__(self, posicionX, posicionY, viajesTotales, viajesActuales, tipoDeCarga, equipo, estado):
        super().__init__(posicionX, posicionY, 3, 3, "todo", equipo, "activo")