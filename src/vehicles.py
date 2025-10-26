from pathfinding import bfs
from resources import Persona, Recurso # Importar para isinstance checks y type hinting en buscar_recurso_mas_cercano
import math 

# Atributos de map_manager
CELL_SIZE = 10
# OFFSET_COL y OFFSET_FILA han sido eliminadas ya que BFS usa coordenadas globales

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

        self.equipo = equipo
        self.estado = estado
        self.camino = []       # Lista de pasos a recorrer (en coordenadas de grid GLOBAL)
        self.objetivos_pendientes = []
        self.objetivo_actual = None    # Destino actual (fila, columna de GRILLE GLOBAL)
        self.velocidad = CELL_SIZE     # píxeles por frame (movimiento suave)
        self.search_cooldown = 0  # Contador de ticks para evitar búsquedas de recursos repetitivas y costosas.

    @property
    def columna(self):
        """Devuelve la COLUMNA GLOBAL de la cuadrícula (0 a 159), calculada desde PX."""
        return int(self.px // CELL_SIZE)

    @property
    def fila(self):
        """Devuelve la FILA GLOBAL de la cuadrícula (0 a 119), calculada desde PY."""
        return int(self.py // CELL_SIZE)

    def explotar(self):
        """Marca el vehículo como inactivo (destruido)."""
        self.estado = "inactivo"
        self.camino = []
        self.objetivo_actual = None
    
    def agregar_objetivo(self, fila, columna):
        # NOTA: Asumimos que fila/columna aquí son coordenadas de la GRILLA GLOBAL (MapManager).
        if len(self.objetivos_pendientes) < self.viajesTotales:
            self.objetivos_pendientes.append((fila, columna))
    
    def actualizar_objetivo(self, grid):
        
        # Si no hay objetivos pendientes, vacía el camino y el objetivo
        if not self.objetivos_pendientes:
            self.camino = []
            self.objetivo_actual = None
            return
        
        # Si llega a su objetivo actual (camino vacío) O no tiene objetivo actual:
        if self.objetivo_actual is None or not self.camino: 
            
            self.objetivo_actual = self.objetivos_pendientes.pop(0)
            
            # Crear una copia de la cuadrícula para el pathfinding al cambiar de objetivo
            temp_grid = [row[:] for row in grid]
            
            # Asegurar que el punto de destino sea 0 en la copia temporal (si fuera un Recurso, por ejemplo)
            destino_fila, destino_col = self.objetivo_actual
            if isinstance(temp_grid[destino_fila][destino_col], Recurso):
                temp_grid[destino_fila][destino_col] = 0
                
            self.calcular_camino(temp_grid, self.objetivo_actual)
    
    def calcular_camino(self, grid, destino):
        """Calcula el camino más corto hacia un destino (fila, columna) usando BFS."""
        start = (self.fila, self.columna) 
        self.camino = bfs(grid, start, destino)
    
    # *** FUNCIÓN CORREGIDA (Eliminación de doble offset) ***
    def mover_por_camino(self):
        if not self.camino:
            return
        
        # El camino [0] contiene la coordenada GLOBAL (fila_global, col_global)
        fila_global, col_global = self.camino[0]

        # 2. Convertir la posición de GRILLA GLOBAL a PÍXELES de destino
        objetivoX = col_global * CELL_SIZE 
        objetivoY = fila_global * CELL_SIZE
        
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
        
        # Si llegamos a la celda (en coordenadas de GRILLE)
        if self.columna == col_global and self.fila == fila_global:
            self.camino.pop(0)
            
            # Aseguramos que las coordenadas de píxeles sean exactas al centro de la celda
            # (aunque el chequeo por grid es más robusto)
            self.px = objetivoX
            self.py = objetivoY

    # *** FUNCIÓN CORREGIDA (Usa Fila Central Fija y FIX de BFS) ***
    def volver_a_base(self, grid):
        """
        Asigna un camino de vuelta a un punto central de la base del vehículo.
        """
        # Usamos una fila central fija (aprox. la mitad de 10 a 79)
        BASE_CENTRAL_FILA = 45 
        
        if self.equipo == "Rojo":
            # Coordenada Global (Fila 45, Columna 15) para Base Roja
            destino_grid = (BASE_CENTRAL_FILA, 15) 
        elif self.equipo == "Azul":
            # Coordenada Global (Fila 45, Columna 145) para Base Azul
            destino_grid = (BASE_CENTRAL_FILA, 145)
        else:
            return
            
        self.objetivo_actual = destino_grid
        
        # --- FIX DE BFS: HACER EL DESTINO ALCANZABLE ---
        # 1. Crear una copia de la cuadrícula
        temp_grid = [row[:] for row in grid]
        
        # 2. Asegurar que el punto de destino de la base sea accesible (marcarlo como 0)
        destino_fila, destino_col = destino_grid
        temp_grid[destino_fila][destino_col] = 0

        # 3. Calcular el camino con la cuadrícula temporal
        self.calcular_camino(temp_grid, destino_grid)
   
    # *** FUNCIÓN CORREGIDA (FIX de BFS al buscar recursos) ***
    def buscar_recurso_mas_cercano(self, grid):
            """
            Busca el recurso más cercano en la grid al que el vehículo puede ir.
            """
            start = (self.fila, self.columna) 
            filas, cols = len(grid), len(grid[0])
            
            if self.viajesActuales <= 0:
                return None
                
            recursos_disponibles = []
            
            # 1. Recorrer la grid para encontrar todos los recursos disponibles y compatibles
            for f in range(filas):
                for c in range(cols):
                    celda_valor = grid[f][c]
                    
                    # Un recurso es una instancia de Recurso (que tiene el atributo 'puntos')
                    if isinstance(celda_valor, Recurso):
                        recurso = celda_valor
                        
                        # 2. Aplicar restricción de carga/tipo de vehículo:
                        if self.carga == "todo" or (self.carga == "personas" and isinstance(recurso, Persona)):
                            recursos_disponibles.append(((f, c), recurso))
                            
            if not recursos_disponibles:
                return None # No hay recursos en el mapa compatibles
                
            # 3. Encontrar el recurso más cercano usando BFS
            mejor_destino = None
            camino_mas_corto = None
            min_longitud = float('inf')

            for (destino_fila, destino_col), recurso in recursos_disponibles:
                destino = (destino_fila, destino_col)
                
                # --- FIX DE BFS: HACER EL RECURSO ALCANZABLE ---
                # 1. Crear una copia de la cuadrícula para el pathfinding
                temp_grid = [row[:] for row in grid] 
                
                # 2. Marcar la celda del recurso de destino como LIBRE (0) en la copia temporal
                # Esto permite que el BFS entre a la celda.
                temp_grid[destino_fila][destino_col] = 0
                
                # 3. Usar la cuadrícula TEMPORAL para calcular el camino.
                camino = bfs(temp_grid, start, destino)
                
                # --- FIN DEL FIX ---
                
                if camino:
                    longitud = len(camino)
                    if longitud < min_longitud:
                        min_longitud = longitud
                        mejor_destino = destino
                        camino_mas_corto = camino
            
            # 4. Asignar el camino y el objetivo
            if mejor_destino:
                self.camino = camino_mas_corto
                self.objetivo_actual = mejor_destino
                return mejor_destino
            else:
                return None
# ----- Subclases (se mantienen igual) -----

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