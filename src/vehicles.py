# vehicles.py (OPTIMIZADO CON A-STAR Y SIN COPIA DE GRID)

# Importamos a_star en lugar de bfs
from pathfinding import a_star, bfs_multiple_destino
from resources import Persona, Recurso
import math 

# Atributos de map_manager
CELL_SIZE = 5

class vehicle:    
    def __init__(self, px, py, viajesTotales, tipoDeCarga, equipo, viajesActuales=None, estado="activo"):
        
        # Coordenadas de PÍXELES
        self.px = px
        self.py = py

        self.carga = tipoDeCarga
        self.viajesTotales = viajesTotales
        
        if viajesActuales is None:
            self.viajesActuales = viajesTotales
        else:
            self.viajesActuales = viajesActuales

        self.recursos = []
        self.equipo = equipo
        self.estado = estado
        self.camino = []
        self.objetivos_pendientes = []
        self.objetivo_actual = None
        self.velocidad = 2
        self.search_cooldown = 0

    @property
    def columna(self):
        """Devuelve la COLUMNA GLOBAL de la cuadrícula (0 a 159), calculada desde PX."""
        return int(self.px // CELL_SIZE)

    @property
    def fila(self):
        """Devuelve la FILA GLOBAL de la cuadrícula (0 a 119), calculada desde PY."""
        return int(self.py // CELL_SIZE)

    def explotar(self):
        """Marca el vehículo como inactivo"""
        self.estado = "inactivo"
        self.camino = []
        self.objetivo_actual = None
        self.equipo= None
        
    
    def agregar_objetivo(self, fila, columna):
        # Asumimos que fila/columna aquí son coordenadas de la GRILLA GLOBAL.
        if len(self.objetivos_pendientes) < self.viajesTotales:
            self.objetivos_pendientes.append((fila, columna))
    

    def actualizar_objetivo(self, grid):
        """
        Replanifica el camino SOLO cuando el vehículo llega a su objetivo final 
        o si no tiene camino y sí tiene un objetivo.
        """
        
        # Si no hay objetivos pendientes ni objetivo actual
        if not self.objetivos_pendientes and not self.objetivo_actual:
            self.camino = []
            self.objetivo_actual = None
            return
        
        # Si no tiene objetivo actual o llegó a su destino 
        if self.objetivo_actual is None or not self.camino: 
            
            # 1. Solo si no tenemos camino, tomamos el siguiente objetivo.
            if not self.camino and self.objetivo_actual:
                # Si hemos llegado A LA CELDA del objetivo, lo marcamos como completado.
                if self.fila == self.objetivo_actual[0] and self.columna == self.objetivo_actual[1]:
                    self.objetivo_actual = None
                    
            # 2. Solo si el objetivo anterior es None, toma el siguiente.
            if self.objetivo_actual is None:
                # Si hay objetivos en cola, toma el siguiente
                if self.objetivos_pendientes:
                    self.objetivo_actual = self.objetivos_pendientes.pop(0)
                else:
                    self.objetivo_actual = None
                    return
            
            # 2. Si el vehículo tiene un objetivo (nuevo o viejo), RE-CALCULA el camino
            if self.objetivo_actual:
                # Usamos la matriz original (grid) y A*
                self.calcular_camino(grid, self.objetivo_actual)
    

    def calcular_camino(self, grid, destino):
        """Calcula el camino más corto hacia un destino (fila, columna) usando A*."""
        start = (self.fila, self.columna) 
        self.camino = a_star(grid, start, destino)
    

    def mover_por_camino(self):
        """Movimiento del auto por la grid."""
        if not self.camino:
            return
        
        fila_global, col_global = self.camino[0]
        objetivoX = col_global * CELL_SIZE 
        objetivoY = fila_global * CELL_SIZE
        
        # --- 1. Movimiento en X (Usando min para limitar el paso) ---
        if self.px < objetivoX:
            # Movemos la cantidad mínima entre la velocidad y la distancia restante.
            move_amount = min(self.velocidad, objetivoX - self.px)
            self.px += move_amount
        elif self.px > objetivoX:
            # Movemos la cantidad mínima entre la velocidad y la distancia restante.
            move_amount = min(self.velocidad, self.px - objetivoX)
            self.px -= move_amount
    
        # --- 2. Movimiento en Y (Usando min para limitar el paso) ---
        if self.py < objetivoY:
            move_amount = min(self.velocidad, objetivoY - self.py)
            self.py += move_amount
        elif self.py > objetivoY:
            move_amount = min(self.velocidad, self.py - objetivoY)
            self.py -= move_amount
    
        # --- 3. Comprobación de Llegada ---
        # Si las coordenadas de píxeles coinciden exactamente, hemos llegado.
        if self.px == objetivoX and self.py == objetivoY:
            self.camino.pop(0)
            # Las siguientes líneas son técnicamente redundantes pero mantienen la consistencia
            self.px = objetivoX
            self.py = objetivoY

    def liberar_recurso(self, grid):
        """'Liberamos' el recurso que encontramos -> Le sacamos su condicion de buscado"""
        if self.objetivo_actual:
            target_fila, target_col = self.objetivo_actual
            recurso_objetivo = grid[target_fila][target_col]
            if isinstance(recurso_objetivo, Recurso) and self.equipo in recurso_objetivo.buscado:
                    recurso_objetivo.buscado.remove(self.equipo) 


    def volver_a_base(self, grid):
        """
        Asigna un camino de vuelta a un punto central de la base del vehículo.
        """
        BASE_CENTRAL_FILA = 45 
        
        if self.equipo == "Rojo":
            destino_grid = (BASE_CENTRAL_FILA, 15) 
        elif self.equipo == "Azul":
            destino_grid = (BASE_CENTRAL_FILA, 145)
        else:
            return
            
        self.objetivo_actual = destino_grid
        
        self.calcular_camino(grid, destino_grid)

    def buscar_recurso_mas_cercano(self, grid):
            """
            Busca el recurso más cercano en la grid al que el vehículo puede ir 
            usando una sola pasada de BFS.
            """
            # Esta función mantiene la copia de grid y BFS Múltiple
            # porque la lógica de A* Múltiple es más compleja.
            # El cooldown en game_engine mitiga su costo.
            start = (self.fila, self.columna) 
            filas, cols = len(grid), len(grid[0])
            
            if self.viajesActuales <= 0:
                return None
                
            recursos_disponibles_pos = []
            
            for f in range(filas):
                for c in range(cols):
                    celda_valor = grid[f][c]
                    
                    if isinstance(celda_valor, Recurso):
                        recurso = celda_valor
                        if self.equipo not in recurso.buscado:
                            if self.carga == "todo" or (self.carga == "personas" and isinstance(recurso, Persona)):
                                recursos_disponibles_pos.append((f, c))
            if not recursos_disponibles_pos:
                return None
                
            # Prepararamos la grid para la búsqueda.
            temp_grid = [row[:] for row in grid] 
            for f, c in recursos_disponibles_pos:
                temp_grid[f][c] = 0 
            
            # Llamar a la función optimizada de BFS Múltiple
            mejor_destino, camino_mas_corto = bfs_multiple_destino(temp_grid, start, recursos_disponibles_pos, self.viajesTotales)
            
            if mejor_destino:
                self.camino = camino_mas_corto
                self.objetivo_actual = mejor_destino
                recurso_objetivo = grid[mejor_destino[0]][mejor_destino[1]]
                if isinstance(recurso_objetivo, Recurso):
                    recurso_objetivo.buscado.append(self.equipo)
                return mejor_destino
            else:
                return None
    
# ----- Subclases -----

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