from pathfinding import bfs

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
        self.camino = []       # Lista de pasos a recorrer (en coordenadas de grid)
        self.objetivos_pendientes = []
        self.objetivo_actual = None   # Destino actual (fila, columna)
        self.velocidad = 2     # píxeles por frame (movimiento suave)

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
        
    
    def agregar_objetivo(self, fila, columna):
        # agrega un objetivo a la lista de objetivos solo si está dentro de su capacidad.
        if len(self.objetivos_pendientes) < self.viajesTotales:
            self.objetivos_pendientes.append((fila, columna))
    
    def actualizar_objetivo(self, grid):
        #*
        # Verifica si el vehículo llegó al objetivo actual.
        # Si llegó, pasa al siguiente y calcula el camino BFS.
        # #
        if not self.objetivos_pendientes:
            self.camino = []
            self.objetivo = None
            return
    
        # Si no hay objetivo actual o se completó el anterior
        # self.posicionY // 5 y self.posicionX // 5 convierten píxeles a coordenadas de grid (si cada celda = 5 píxeles).
        if self.objetivo_actual is None or (self.posicionY // 5, self.posicionX // 5) == self.objetivo_actual: 
            self.objetivo_actual = self.objetivos_pendientes.pop(0)  # toma el siguiente objetivo.
            self.calcular_camino(grid, self.objetivo_actual)  # calcula el camino BFS.
    
    def calcular_camino(self, grid, destino):
        #*
        #Calcula el camino más corto usando BFS desde la posición actual hasta 'destino'.
        #La posición actual se pasa como coordenadas de grid (fila, columna).
        # #
        start = (self.posicionY, self.posicionX)  # fila, columna
        self.camino = bfs(grid, start, destino)
    
    def mover_por_camino(self):
        #*
        # Mueve el vehículo hacia la siguiente celda del camino usando su velocidad.
        # #
        if not self.camino:
            return
        
        fila, col = self.camino[0]  # primera posición del BFS
        objetivoX = col * 5
        objetivoY = fila * 5

        # Mover en X
        # min(self.velocidad, self.posicionX - objetivoX) asegura que no se pase del objetivo
        if self.posicionX < objetivoX:
            self.posicionX += min(self.velocidad, objetivoX - self.posicionX) # sumamos para ir a la derecha
        elif self.posicionX > objetivoX:
            self.posicionX -= min(self.velocidad, self.posicionX - objetivoX) # restamos para ir a la izquierda
        
        # Mover en Y
        if self.posicionY < objetivoY:
            self.posicionY += min(self.velocidad, objetivoY - self.posicionY) # sumamos para ir arriba
        elif self.posicionY > objetivoY:
            self.posicionY -= min(self.velocidad, self.posicionY - objetivoY) # sumamos para ir abajo
        
        # Si llegamos a la celda
        if self.posicionX == objetivoX and self.posicionY == objetivoY:
            self.camino.pop(0)
    
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