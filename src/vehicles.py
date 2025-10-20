# src/vehicles.py
from pathfinding import bfs
from map_manager import MapManager

mmanager= MapManager()
class vehicle:    
    def __init__(self, px, py, viajesTotales, tipoDeCarga, equipo, viajesActuales=None, estado="activo"):
        # Argumentos: columna y fila son coordenadas de GRILLA (ej: 1, 60)

        #Coordenadas en la GRILLA (para pathfinding)
        self.grid_col = px //mmanager.CELL_SIZE
        self.grid_fila = py //mmanager.CELL_SIZE
        
        #Coordenadas de PÍXELES (para dibujar y movimiento suave)
        # Se inicializan a la posición de píxeles correspondiente a la grilla:
        self.px = px  # Posición X en píxeles
        self.py = py  # Posición Y en píxeles

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
        self.objetivo_actual = None    # Destino actual (fila, columna de GRILLE)
        self.velocidad = mmanager.CELL_SIZE     # píxeles por frame (movimiento suave)

    def explotar(self):
        self.estado = "explotado"

    # MOVIMIENTO (OBSOLETO)
    def irArriba(self):
        self.py -= self.velocidad
    def irAbajo(self):
        self.py += self.velocidad
    def irDerecha(self):
        self.px += self.velocidad
    def irIzquierda(self):
        self.px -= self.velocidad
    
    
    def agregar_objetivo(self, fila, columna):
        if len(self.objetivos_pendientes) < self.viajesTotales:
            self.objetivos_pendientes.append((fila, columna))
    
    def actualizar_objetivo(self, grid):
        # El chequeo se hace con la posición en PÍXELES convertida a GRILLA
        if not self.objetivos_pendientes:
            self.camino = []
            self.objetivo_actual = None
            return
        
        if self.objetivo_actual is None or \
           (self.py // self.velocidad, self.px // self.velocidad) == self.objetivo_actual: 
            
            self.objetivo_actual = self.objetivos_pendientes.pop(0)
            
            # Actualiza la posición de grilla para reflejar dónde está ahora el vehículo:
            self.grid_fila = self.py // self.velocidad
            self.grid_col = self.px // self.velocidad
            
            self.calcular_camino(grid, self.objetivo_actual)
    
    def calcular_camino(self, grid, destino):
        # La posición inicial DEBE ser la posición de GRILLA.
        start = (self.grid_fila, self.grid_col)  
        self.camino = bfs(grid, start, destino)
    
    def mover_por_camino(self):
        if not self.camino:
            return
        
        fila_local, col_local = self.camino[0]  # Posición LOCAL de la cuadrícula [0-98, 0-68]
        
        # -------------------------------------------------------------
        # --- CORRECCIÓN CRÍTICA: Convertir de LOCAL a GLOBAL a PÍXEL ---
        
        OFFSET_COL = MapManager.TERRAIN_CONFIG_GRID["min_col"] # Es 30
        OFFSET_FILA = MapManager.TERRAIN_CONFIG_GRID["min_row"] # Es 10
        
        # 1. Convertir la posición de la grilla LOCAL a la posición de GRILLA GLOBAL
        fila_global = fila_local + OFFSET_FILA
        col_global = col_local + OFFSET_COL
        
        # 2. Convertir la posición de GRILLA GLOBAL a PÍXELES de destino
        objetivoX = col_global * 5 
        objetivoY = fila_global * 5
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
            # Sincronizamos las coordenadas de cuadrícula con la posición LOCAL
            self.grid_col = col_local # Ahora almacena la columna LOCAL
            self.grid_fila = fila_local # Ahora almacena la fila LOCAL
                
# ----- Subclases -----
# Se corrige el constructor para que los argumentos concuerden con el padre.

class jeep(vehicle):
    CAPACIDAD = 2
    TIPO_CARGA = "todo"
    
    def __init__(self, px, py, equipo): # <-- Argumentos son columna/fila de GRILLA
        super().__init__(
            px=px, 
            py=py, 
            equipo=equipo,
            viajesTotales=self.CAPACIDAD, 
            tipoDeCarga=self.TIPO_CARGA
        )
# Haz este mismo cambio en moto, auto, y camion.

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