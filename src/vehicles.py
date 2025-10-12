class vehicle:    
    def __init__(self, posicionX, posicionY, viajesTotales, tipoDeCarga, equipo, viajesActuales=None, estado="activo"):
        #los viajes totales también son la capacacidad

        self.posicionX = posicionX
        self.posicionY = posicionY
        self.carga = tipoDeCarga
        self.viajesTotales = viajesTotales
        
        if viajesActuales is None:
            self.viajesActuales = viajesTotales
        else:
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


class jeep(vehicle):
    CAPACIDAD = 2
    TIPO_CARGA = "todo"
    
    def __init__(self, posicionX, posicionY, equipo):
        super().__init__(
            posicionX=posicionX, 
            posicionY=posicionY, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )

class moto(vehicle):
    CAPACIDAD = 1
    TIPO_CARGA = "personas"
    
    def __init__(self, posicionX, posicionY, equipo):
        super().__init__(
            posicionX=posicionX, 
            posicionY=posicionY, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )

class auto(vehicle):
    CAPACIDAD = 1
    TIPO_CARGA = "todo"
    
    def __init__(self, posicionX, posicionY, equipo):
        super().__init__(
            posicionX=posicionX, 
            posicionY=posicionY, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )

class camion(vehicle):
    CAPACIDAD = 3
    TIPO_CARGA = "todo"
    
    def __init__(self, posicionX, posicionY, equipo):
        super().__init__(
            posicionX=posicionX, 
            posicionY=posicionY, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )