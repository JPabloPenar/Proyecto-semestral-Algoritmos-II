from pathfinding import bfs

#Atributos de map_manager
CELL_SIZE = 5
OFFSET_COL = 30  #Antes en lugar de hacer esto se hacía import map_manager, pero causaba un ciclo porque en map_manager también se necesita acceder a vehicle
OFFSET_FILA = 10



class vehicle:    
    def __init__(self, px, py, viajesTotales, tipoDeCarga, equipo, viajesActuales=None, estado="activo"):
        
        # Coordenadas de PÍXELES (fuente de verdad del movimiento)
        self.px = px  # Posición X en píxeles
        self.py = py  # Posición Y en píxeles

        self.carga = tipoDeCarga
        self.viajesTotales = viajesTotales
        
        if viajesActuales is None:
            self.viajesActuales = viajesTotales
        else:
            self.viajesActuales = viajesActuales

        self.recursos = []
        self.equipo = equipo
        self.estado = estado
        self.camino = []       # Lista de pasos a recorrer (en coordenadas de grid LOCALES)
        self.objetivos_pendientes = []
        self.objetivo_actual = None    # Destino actual (fila, columna de GRILLE GLOBAL)
        self.velocidad = CELL_SIZE     # píxeles por frame (movimiento suave)

    @property
    def columna(self):
        """Devuelve la COLUMNA GLOBAL de la cuadrícula (0 a 159), calculada desde PX."""
        # Se usa para MapManager (colisiones) y Pathfinding (inicio).
        return int(self.px // CELL_SIZE)

    @property
    def fila(self):
        """Devuelve la FILA GLOBAL de la cuadrícula (0 a 119), calculada desde PY."""
        # Se usa para MapManager (colisiones) y Pathfinding (inicio).
        return int(self.py // CELL_SIZE)

    def explotar(self):
        self.estado = "explotado"
    
    def agregar_objetivo(self, fila, columna):
        # NOTA: Asumimos que fila/columna aquí son coordenadas de la GRILLA GLOBAL (MapManager).
        if len(self.objetivos_pendientes) < self.viajesTotales:
            self.objetivos_pendientes.append((fila, columna))
    
    def actualizar_objetivo(self, grid):
        
        if not self.objetivos_pendientes:
            self.camino = []
            self.objetivo_actual = None
            return
        
        if self.objetivo_actual is None or (self.fila, self.columna) == self.objetivo_actual: 
            
            self.objetivo_actual = self.objetivos_pendientes.pop(0)
            self.calcular_camino(grid, self.objetivo_actual)
    
    def calcular_camino(self, grid, destino):
        start = (self.fila, self.columna) 
        self.camino = bfs(grid, start, destino)
    
    def mover_por_camino(self):
        if not self.camino:
            return
        
        # El camino [0] contiene la coordenada LOCAL (fila_local, col_local) calculada por BFS
        # RELATIVA al terreno de acción (0,0)
        fila_local, col_local = self.camino[0]
        

        fila_global = fila_local + OFFSET_FILA
        col_global = col_local + OFFSET_COL
        
        # 2. Convertir la posición de GRILLA GLOBAL a PÍXELES de destino
        objetivoX = col_global * CELL_SIZE 
        objetivoY = fila_global * CELL_SIZE 
        # -------------------------------------------------------------

        # Mover en X (usando la posición en PÍXELES)
        if self.px < objetivoX:
            self.px += self.velocidad
        elif self.px > objetivoX:
            self.px -= self.velocidad
        
        # Mover en Y (usando la posición en PÍXELES)
        if self.py < objetivoY:
            self.py += self.velocidad
        elif self.py > objetivoY:
            self.py -= self.velocidad
        
        # Si llegamos a la celda (en PÍXELES)
        if self.px == objetivoX and self.py == objetivoY:
            self.camino.pop(0)
            
            # Aseguramos que las coordenadas de píxeles sean exactas al centro de la celda
            self.px = objetivoX
            self.py = objetivoY
                
# ----- Subclases (se mantienen igual, solo usan el nuevo constructor) -----

class jeep(vehicle):
    CAPACIDAD = 2
    TIPO_CARGA = "todo"
    
    def __init__(self, px, py, equipo): 
        super().__init__(
            px=px, 
            py=py, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )

class moto(vehicle):
    CAPACIDAD = 1
    TIPO_CARGA = "personas"
    
    def __init__(self, px, py, equipo): 
        super().__init__(
            px=px, 
            py=py, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )

class auto(vehicle):
    CAPACIDAD = 1
    TIPO_CARGA = "todo"
    
    def __init__(self, px, py, equipo):
        super().__init__(
            px=px, 
            py=py, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )

class camion(vehicle):
    CAPACIDAD = 3
    TIPO_CARGA = "todo"
    
    def __init__(self, px, py, equipo):
        super().__init__(
            px=px, 
            py=py, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )