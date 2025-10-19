import random
import math
from mines import MinaO1, MinaO2, MinaT1, MinaT2, MinaG1, Mina
from resources import Persona, Ropa, Alimentos, Medicamentos, Armamentos, Recurso
from vehicles import vehicle

class MapManager:
    
    CELL_SIZE = 5 # Píxeles por unidad de cuadrícula (grid)
    
    BORDER_MARGIN = 40 

    # NUEVA CONFIGURACIÓN: Dimensiones de la Ventana en Unidades de Grid
    GRID_FILAS_TOTALES = 600 // CELL_SIZE  # 120
    GRID_COLS_TOTALES = 800 // CELL_SIZE   # 160
    
    TERRAIN_CONFIG_GRID = {
        "min_col": 150 // CELL_SIZE, 
        "max_col": (650 // CELL_SIZE) - 1, 
        "min_row": 50 // CELL_SIZE, 
        "max_row": (400 // CELL_SIZE) - 1
    }
    
    BORDER_MARGIN_GRID = BORDER_MARGIN // CELL_SIZE 
    
    # Cuadrícula de Acción Final (Unidades de Cuadrícula)
    ACTION_GRID_CONFIG = {
        "min_col": TERRAIN_CONFIG_GRID["min_col"] + BORDER_MARGIN_GRID,
        "max_col": TERRAIN_CONFIG_GRID["max_col"] - BORDER_MARGIN_GRID,
        "min_row": TERRAIN_CONFIG_GRID["min_row"] + BORDER_MARGIN_GRID,
        "max_row": TERRAIN_CONFIG_GRID["max_row"] - BORDER_MARGIN_GRID,
    }


    # Definición de las zonas de las bases para exclusión de minas/recursos
    # y para la comprobación de destino/base (para descarga).
    BASE1_GRID = { # (0 a 150 px) / 5 -> col 0 a 30
        "min_col": 0,
        "max_col": 150 // CELL_SIZE - 1, # 29
        "min_row": 50 // CELL_SIZE, # 10
        "max_row": 400 // CELL_SIZE - 1 # 79
    }
    
    BASE2_GRID = { # (650 a 800 px) / 5 -> col 130 a 159
        "min_col": 650 // CELL_SIZE, # 130
        "max_col": GRID_COLS_TOTALES - 1, # 159
        "min_row": 50 // CELL_SIZE, # 10
        "max_row": 400 // CELL_SIZE - 1 # 79
    }


    def _crear_grid(self, filas, columnas):
        # 0 = libre, 1 = obstáculo/mina (usado por BFS)
        return [[0 for _ in range(columnas)] for _ in range(filas)]


    # GRID_MAESTRA (120x160) - Ahora se inicializa en __init__
    # GRID_TERRENO (Ya no es necesaria si usamos la maestra)
    #GRID_TERRENO= _crear_grid(TERRAIN_CONFIG_GRID["max_row"]-TERRAIN_CONFIG_GRID["min_row"], TERRAIN_CONFIG_GRID["max_col"]-TERRAIN_CONFIG_GRID["min_col"])
    

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
        # Inicializa la GRID MAESTRA para pathfinding (incluye bases y terreno)
        self.grid_maestra = self._crear_grid(self.GRID_FILAS_TOTALES, self.GRID_COLS_TOTALES)

        # RASTREO DE POSICIÓN ANTERIOR DE MINA MÓVIL
        self.old_mobile_mine_fila = -1
        self.old_mobile_mine_col = -1
        self._initial_placement_done = False # Bandera para la primera colocación


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

        SAFETY_MARGIN_GRID = 1.5

        for entity in self.entities:
            
            # --- 1. Chequeo de colisión entre MINAS y MINAS ---
            if isinstance(entity, Mina) and isinstance(new_entity, Mina):

                SUMA_RADIOS = entity.radio + new_entity.radio
                
                
                # Minas Circulares (O1, O2)
                if entity.tipo in ["O1", "O2"]:
                    # Distancia entre centros de celdas de grid (teorema de Pitágoras)
                    distance = math.sqrt((entity.columna - col)**2 + (entity.fila - fila)**2)
                    # La distancia de separación debe ser mayor al radio de efecto en grid, más un margen
                    if distance < SUMA_RADIOS + SAFETY_MARGIN_GRID: 
                        return True

                # Mina T1 (Horizontal)
                elif entity.tipo == "T1":
                    # Colisión si la nueva entidad cae dentro de la franja vertical de la mina
                    if abs(entity.fila - fila) < entity.radio + SAFETY_MARGIN_GRID:
                        return True
                        
                # Mina T2 (Vertical) - Chequea distancia en X (columna)
                elif entity.tipo == "T2":
                    # Colisión si la nueva entidad cae dentro de la franja horizontal de la mina
                    if abs(entity.columna - col) < entity.radio + SAFETY_MARGIN_GRID:
                        return True
            
            # Chequeo de colisión entre MINAS y RECURSOS
            elif isinstance(entity, Mina) and isinstance(new_entity, Recurso):
                
                # Minas Circulares (O1, O2)
                if entity.tipo in ["O1", "O2"]:
                    distance = math.sqrt((entity.columna - col)**2 + (entity.fila - fila)**2)
                    if distance < entity.radio + SAFETY_MARGIN_GRID: 
                        return True
                        
                # Mina T1 (Horizontal)
                elif entity.tipo == "T1":
                    distance_y = abs(entity.fila - fila)
                    if distance_y < entity.radio + SAFETY_MARGIN_GRID:
                        return True
                        
                # Mina T2 (Vertical)
                elif entity.tipo == "T2":
                    distance_x = abs(entity.columna - col)
                    if distance_x < entity.radio + SAFETY_MARGIN_GRID:
                        return True
                    
            # --- NUEVO CHEQUEO: MINA MÓVIL vs. RECURSO EXISTENTE ---
            # Verifica si una nueva mina (Mina G1, que se reubica) colisiona con un Recurso existente
            elif isinstance(entity, Recurso) and isinstance(new_entity, Mina):
                # Usamos el radio de la nueva mina (G1) como área a evitar en torno al Recurso.
                # Colisión circular (distancia del centro del recurso al centro de la mina)
                distance = math.sqrt((entity.columna - col)**2 + (entity.fila - fila)**2)
                
                # Colisión si la distancia es menor al radio de la mina G1 + margen
                if distance < new_entity.radio + SAFETY_MARGIN_GRID: 
                    return True
                                       
            # --- 2. Chequeo de colisión entre RECURSOS (grid units) ---
            if isinstance(new_entity, Recurso) and isinstance(entity, Recurso):
                # Margen pequeño de 1 unidad de grid para evitar apilamiento
                distance = math.sqrt((entity.columna - col)**2 + (entity.fila - fila)**2)
                if distance < 1: 
                    return True
                         
        return False

    def check_vehicle_collisions(self, veh):

        fila, col = veh.fila, veh.columna
        # Primero, verifica que la posición esté dentro de los límites de la grid
        if 0 <= fila < self.GRID_FILAS_TOTALES and 0 <= col < self.GRID_COLS_TOTALES:

            # El objeto en la grid (puede ser 0, 1, o un objeto Recurso)
            entity = self.grid_maestra[fila][col]

            # Colisión con Mina (estática o móvil) - Marcadas con 1 en la grid
            if entity == 1:
                # Distancia en grid_units
                dist_col = abs(entity.columna - veh.columna)
                dist_fila = abs(entity.fila - veh.fila)

                # Colisión por radio:
                if entity.tipo in ["O1", "O2", "G1"]: # Minas Circulares
                    distance = math.sqrt(dist_col**2 + dist_fila**2)
                    if distance <= entity.radio:
                        return entity.tipo, entity

                elif entity.tipo == "T1": # Mina Horizontal
                    if dist_fila <= entity.radio:
                        return entity.tipo, entity

                elif entity.tipo == "T2": # Mina Vertical
                    if dist_col <= entity.radio:
                        return entity.tipo, entity

            elif isinstance(entity, Recurso):
                return "recurso", entity

            elif isinstance(entity, vehicle): 
                return "vehiculo", entity

        return None, None

    def _relocate_mobile_mine(self):
            """
            Reubica la Mina G1 de forma segura (sin colisionar con entidades estáticas).
            Esta función se llama cuando la mina está invisible (transición instantánea).
            """

            placed = False
            attempts = 0
            new_mine = self.mobile_mine
            
            while not placed and attempts < 1000000:
                col, fila = self._get_random_pos()
                
                # Chequeamos colisión contra todas las entidades estáticas
                if not self._check_collision(col, fila, new_mine): 
                    self.mobile_mine.set_posicion(col, fila)
                    placed = True

                attempts += 1
            
            if not placed:
                #col, fila = self._get_random_pos()
                #self.mobile_mine.set_posicion(col, fila)
                print ("error mina movil")


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

                    # Ponemos las minas con 1 en la grid
                    self.grid_maestra[fila][col] = 1

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

                        # Ponemos los objetos en la grid
                        self.grid_maestra[fila][col] = new_resource

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

        # 4. Actualizar la Grid y registrar posición inicial
        self._actualizar_grid_minas() # LLAMA A LA NUEVA FUNCIÓN EFICIENTE
        
        # Registra la posición inicial como "anterior"
        self.old_mobile_mine_fila = self.mobile_mine.fila
        self.old_mobile_mine_col = self.mobile_mine.columna
        self._initial_placement_done = True


    def _actualizar_grid_minas(self):
        """
        Actualiza la GRID MAESTRA SÓLO con la posición de la Mina G1
        sin regenerar toda la matriz.
        """
        
        # Borrar la posición anterior (solo si ya se colocó una vez)
        if self._initial_placement_done:
            # Poner la celda anterior de la mina en 0 (libre)
            self.grid_maestra[self.old_mobile_mine_fila][self.old_mobile_mine_col] = 0
            
            # Nota: Las minas estáticas deben haberse colocado una sola vez en distribute_entities.
            # Por eso esta función solo maneja la Mina G1.

        # Marcar la nueva posición si la mina está visible
        if self.mobile_mine_visible:
            # 1 = obstáculo/mina
            self.grid_maestra[self.mobile_mine.fila][self.mobile_mine.columna] = 1
            
        # Actualizar la posición antigua para el siguiente tick
        self.old_mobile_mine_fila = self.mobile_mine.fila
        self.old_mobile_mine_col = self.mobile_mine.columna




    RELOCATION_TICK = 100
    def update_time(self):
        self.time_instance += 1
        
        if self.is_relocating:
            # Pasa 1 tick invisible (instantáneo)
            # 1. Se reubica la posición
            self._relocate_mobile_mine()

            # 2. Se vuelve visible
            self.mobile_mine_visible = True
            self.is_relocating = False

            # 3. Se actualiza la grid (borra la posición anterior y marca la nueva)
            self._actualizar_grid_minas()
            
        elif self.time_instance % self.RELOCATION_TICK == 0:
            # Tick donde debe moverse (Pasa 1 tick visible -> 1 tick invisible)

            # La mina desaparece y se registra su posición actual como la que debe ser borrada
            self.mobile_mine_visible = False

            # Se actualiza la grid (borra la posición actual y no marca la nueva - sigue invisible)
            self._actualizar_grid_minas()

            self.is_relocating = True   # Prepara la reubicación para el siguiente tick
        
        return self.time_instance