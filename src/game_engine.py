import random
import math
from mines import MinaO1, MinaO2, MinaT1, MinaT2, MinaG1, Mina
from resources import Persona, Ropa, Alimentos, Medicamentos, Armamentos, Recurso

class GameEngine:
    
    CELL_SIZE = 5 # Píxeles por unidad de cuadrícula (grid)
    
    BORDER_MARGIN = 20 
    
    TERRAIN_CONFIG_GRID = {
        "min_col": 150 // CELL_SIZE + BORDER_MARGIN, 
        "max_col": 650 // CELL_SIZE + BORDER_MARGIN, 
        "min_row": 50 // CELL_SIZE + BORDER_MARGIN, 
        "max_row": 400 // CELL_SIZE + BORDER_MARGIN
    }
    
    BORDER_MARGIN_GRID = BORDER_MARGIN // CELL_SIZE
    
    # Cuadrícula de Acción Final (Unidades de Cuadrícula)
    ACTION_GRID_CONFIG = {
        "min_col": TERRAIN_CONFIG_GRID["min_col"] + BORDER_MARGIN_GRID,
        "max_col": TERRAIN_CONFIG_GRID["max_col"] - BORDER_MARGIN_GRID,
        "min_row": TERRAIN_CONFIG_GRID["min_row"] + BORDER_MARGIN_GRID,
        "max_row": TERRAIN_CONFIG_GRID["max_row"] - BORDER_MARGIN_GRID,
    }

   
    # Clase de Mina Móvil y Estáticas 
    MINE_CLASSES = [MinaO1, MinaO2, MinaT1, MinaT2] 
    MOBILE_MINE_CLASS = MinaG1
    
    # Distribución de Recursos 
    RESOURCE_DISTRIBUTION = {
        Persona: 10,
        Ropa: 10,
        Alimentos: 10,
        Medicamentos: 10,
        Armamentos: 10
    }
    
    def __init__(self):
        self.entities = [] 
        self.mobile_mine = self.MOBILE_MINE_CLASS(id_=99)
        self.time_instance = 0
        self.mobile_mine_visible = False
        self.is_relocating = False


    def _get_random_pos(self):
        """Genera una posición aleatoria de GRID (columna, fila) dentro del Terreno de Acción con margen."""
        col = random.randint(self.ACTION_GRID_CONFIG["min_col"], self.ACTION_GRID_CONFIG["max_col"])
        fila = random.randint(self.ACTION_GRID_CONFIG["min_row"], self.ACTION_GRID_CONFIG["max_row"])
        return col, fila # Retorna (columna, fila)


    def _check_collision(self, col, fila, new_entity):
        """
        Verifica si la posición (x, y) choca con el área de efecto o posición
        de una entidad estática existente (mina o recurso).
        """

        SAFETY_MARGIN_GRID = 2

        for entity in self.entities:
            
            # --- 1. Chequeo de colisión entre MINAS y nuevas entidades ---
            if isinstance(entity, Mina):
                
                # Convertir el radio original (en píxeles/distancia) a unidades de grid
                GRID_RADIUS = entity.radio / self.CELL_SIZE
                
                
                
                # Minas Circulares (O1, O2)
                if entity.tipo in ["O1", "O2"]:
                    # Distancia entre centros de celdas de grid (teorema de Pitágoras)
                    distance = math.sqrt((entity.columna - col)**2 + (entity.fila - fila)**2)
                    # La distancia de separación debe ser mayor al radio de efecto en grid, más un margen
                    if distance < GRID_RADIUS + SAFETY_MARGIN_GRID: 
                        return True

                # Mina T1 (Horizontal)
                elif entity.tipo == "T1":
                    # Colisión si la nueva entidad cae dentro de la franja vertical de la mina
                    if abs(entity.fila - fila) < GRID_RADIUS + SAFETY_MARGIN_GRID:
                        return True
                        
                # Mina T2 (Vertical) - Chequea distancia en X (columna)
                elif entity.tipo == "T2":
                    # Colisión si la nueva entidad cae dentro de la franja horizontal de la mina
                    if abs(entity.columna - col) < GRID_RADIUS + SAFETY_MARGIN_GRID:
                        return True
                    
            # --- 2. Chequeo de colisión entre RECURSOS (grid units) ---
            if isinstance(new_entity, Recurso) and isinstance(entity, Recurso):
                # Margen pequeño de 1 unidad de grid para evitar apilamiento
                distance = math.sqrt((entity.columna - col)**2 + (entity.fila - fila)**2)
                if distance < 1: 
                    return True
                         
        return False

    def _relocate_mobile_mine(self):
            """
            Reubica la Mina G1 de forma segura (sin colisionar con entidades estáticas).
            Esta función se llama cuando la mina está invisible (transición instantánea).
            """

            placed = False
            attempts = 0
            new_mine = self.mobile_mine
            
            while not placed and attempts < 1000:
                col, fila = self._get_random_pos()
                
                # Chequeamos colisión contra todas las entidades estáticas
                if not self._check_collision(col, fila, new_mine): 
                    self.mobile_mine.set_posicion(col, fila)
                    placed = True
                attempts += 1
            
            if not placed:
                col, fila = self._get_random_pos()
                self.mobile_mine.set_posicion(col, fila)

    def distribute_entities(self):

        self.entities = []
        entity_id_counter = 1
        
        # 1. Distribuir Minas Estáticas (aumentamos intentos por mayor restricción de espacio)
        for MineClass in self.MINE_CLASSES:
            placed = False
            attempts = 0
            while not placed and attempts < 5000: # Aumentamos intentos a 5000
                col, fila = self._get_random_pos()
                new_mine = MineClass(id_=entity_id_counter)
                if not self._check_collision(col, fila, new_mine):
                    new_mine.set_posicion(col, fila)
                    self.entities.append(new_mine)
                    entity_id_counter += 1
                    placed = True
                attempts += 1
            if not placed:
                print(f"ERROR CRÍTICO: No se pudo colocar {MineClass.__name__}. Intenta reiniciar el simulador.")
                break # Detener si la colocación falla críticamente

        # 2. Distribuir Recursos (Mantenemos 1000 intentos, menos crítico)
        for ResourceClass, count in self.RESOURCE_DISTRIBUTION.items():
            for _ in range(count):
                placed = False
                attempts = 0
                while not placed and attempts < 1000:
                    col, fila = self._get_random_pos()
                    new_resource = ResourceClass(id_=entity_id_counter)
                    if not self._check_collision(col, fila, new_resource):
                        new_resource.set_posicion(col, fila)
                        self.entities.append(new_resource)
                        entity_id_counter += 1
                        placed = True
                    attempts += 1
                if not placed:
                    print(f"ADVERTENCIA: No se pudo colocar {ResourceClass.__name__}. Espacio lleno o colisión recurrente.")
        
        # 3. Posicionar Mina Móvil (Mina G1)
        self._relocate_mobile_mine() # Llama a la nueva función
        self.mobile_mine_visible = True
        self.time_instance = 0 
        self.is_relocating = False

    RELOCATION_TICK = 100
    def update_time(self):
        self.time_instance += 1
        
        if self.is_relocating:
            # Pasa 1 tick invisible (instantáneo)
            self._relocate_mobile_mine()
            self.mobile_mine_visible = True
            self.is_relocating = False
            
        elif self.time_instance % self.RELOCATION_TICK == 0:
            # Tick donde debe moverse (Pasa 1 tick visible -> 1 tick invisible)
            self.mobile_mine_visible = False
            self.is_relocating = True
        
        return self.time_instance