from pathfinding import bfs

class vehicle:    
    def __init__(self, columna, fila, viajesTotales, tipoDeCarga, equipo, viajesActuales=None, estado="activo"):

        self.columna = columna
        self.fila = fila
        
        self.carga = tipoDeCarga
        self.viajesTotales = viajesTotales
        
        if viajesActuales is None:
            self.viajesActuales = viajesTotales
        else:
            self.viajesActuales = viajesActuales

        self.equipo = equipo
        self.estado = estado
        self.camino = []       
        self.objetivos_pendientes = []
        self.objetivo_actual = None     # Destino actual (fila,columna)  
        self.velocidad = 2     # Pixeles por frame (movimiento suave)

    def explotar(self):
        self.estado = "explotado"

    def recoger(self):
            self.viajesActuales -= 1 
            if self.viajesActuales == 0: # si tiene la carga 
                # volver a base para descargar
                pass

    def descargar(self): # Se completa un viaje y se reestablecen la cantidad de viajes y se le suman los puntos al equipo
        
        self.viajesActuales=self.viajesTotales
        

    # Movimiento. 
    def irArriba(self):
        self.fila -= 1
      
    def irAbajo(self):
        self.fila += 1
        
    def irDerecha(self):
        self.columna += 1
       
    def irIzquierda(self):
        self.columna -= 1
        
    
    def agregar_objetivo(self, fila, columna):
        # agrega un objetivo a la lista de objetivos solo si está dentro de su capacidad.
        if len(self.objetivos_pendientes) < self.viajesTotales:
            self.objetivos_pendientes.append((fila, columna))
    
    def actualizar_objetivo(self, grid):
        #*
        # Verifica si el vehículo llegó al objetivo actual (en coordenadas de grid).
        # Si llegó, pasa al siguiente y calcula el camino BFS.
        # #
        if not self.objetivos_pendientes:
            self.camino = []
            self.objetivo_actual = None # Corregido: antes era 'self.objetivo'
            return
    
        # Si no hay objetivo actual o se completó el anterior.
        if self.objetivo_actual is None or (self.fila, self.columna) == self.objetivo_actual: 
            self.objetivo_actual = self.objetivos_pendientes.pop(0)  # toma el siguiente objetivo.
            self.calcular_camino(grid, self.objetivo_actual)  # calcula el camino BFS.
    
    def calcular_camino(self, grid, destino):
        #*
        # Calcula el camino más corto usando BFS desde la posición actual hasta 'destino'.
        # La posición actual se pasa como coordenadas de grid (fila, columna).
        # #
        start = (self.fila, self.columna)  # fila, columna
        self.camino = bfs(grid, start, destino)
    
    def mover_por_camino(self):
        # Mueve el vehículo hacia la siguiente celda del camino usando su velocidad.
        
        if not self.camino:
            return
        
        # Primera posicion del bfs
        fila_grid, col_grid = self.camino[0]
        

        objetivoX = col_grid * 5
        objetivoY = fila_grid * 5
    
        
        # Opción 1 (Movimiento Instantáneo en Grid):
        self.fila = fila_grid
        self.columna = col_grid
        self.camino.pop(0) # Movimiento instantáneo
    
   

# ----- Subclases -----
class jeep(vehicle):
    CAPACIDAD = 2
    TIPO_CARGA = "todo"
    
    def __init__(self, columna, fila, equipo):
        super().__init__(
            columna=columna, 
            fila=fila, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )

class moto(vehicle):
    CAPACIDAD = 1
    TIPO_CARGA = "personas"
    
    def __init__(self, columna, fila, equipo):
        super().__init__(
            columna=columna, 
            fila=fila, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )

class auto(vehicle):
    CAPACIDAD = 1
    TIPO_CARGA = "todo"
    
    def __init__(self, columna, fila, equipo):
        super().__init__(
            columna=columna, 
            fila=fila, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )

class camion(vehicle):
    CAPACIDAD = 3
    TIPO_CARGA = "todo"
    
    def __init__(self, columna, fila, equipo):
        super().__init__(
            columna=columna, 
            fila=fila, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )