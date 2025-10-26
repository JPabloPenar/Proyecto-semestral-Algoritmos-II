import random
import math
from mines import MinaO1, MinaO2, MinaT1, MinaT2, MinaG1, Mina
from resources import Persona, Ropa, Alimentos, Medicamentos, Armamentos, Recurso
from vehicles import vehicle
import pickle
import os

class MapManager:

    # --- METODOS DE MANEJO DE ESTADOS DE JUEGO ---
    # Serializa y guarda el estado actual del MapManager en un archivo.
    def guardar_estado(self, filename="map_state.pickle"):

        try:
            # acceder al archivo con permisos de donde wb = write binary
            with open(filename, 'wb') as file:

                # Dump se encarga de serializar
                pickle.dump(self, file)

            return True
        except Exception as e:
            print(f"Error al guardar el estado: {e}")
            return False
        
    #Carga y retorna un objeto MapManager desde un archivo serializado.
    def cargar_estado(filename="map_state.pickle"):

        try:
            if not os.path.exists(filename):
                #print(f"Advertencia: Archivo de estado '{filename}' no encontrado.")
                return None
            
            # acceder al archivo con permisos de donde rb = read binary
            with open(filename, 'rb') as file:
                # Carga el objeto completo (incluyendo grid, entities, etc.)
                return pickle.load(file) 
        except Exception as e:
            print(f"Error al cargar el estado: {e}")
            return None

    # Genera el nombre de archivo para un índice de historia específico.
    def _get_history_filename(self, index):

        # .makedirs crea la carpeta si no existe
        os.makedirs(self.base_dir, exist_ok=True) # Asegura que la carpeta exista

        """
        .join une diferentes partes de la ruta de un archivo
        En nuestro caso une: 
        1. self.base_dir(nombre de la carpeta donde se almacenan todos los estados) 
        2. f-string que crea el nombre del archivo (index:04 es un numero entero que debe ser rellenado hasta llegar a 4 digitos)
            I.E: state_0000.pickle
        """
        return os.path.join(self.base_dir, f"state_{index:04d}.pickle")

    # Guarda el estado actual del MapManager como un nuevo paso en la historia.
    def guardar_estado_historial(self):
        
        #esto no hace nada
        #while len(self.history) > self.current_history_index + 1:
            # Eliminar el archivo si existe (para no llenar el disco)
            #filename_to_delete = self.history.pop()
            #if os.path.exists(filename_to_delete):
                #os.remove(filename_to_delete)

        # Guardar el estado actual en el siguiente índice
        self.current_history_index += 1
        filename = self._get_history_filename(self.current_history_index)
        
        if self.guardar_estado(filename):
            self.history.append(filename)
            return True
        
        return False
    
    # Borra todos los archivos .pickle de la carpeta de historial y reinicia el historial interno.
    def _limpiar_historial(self):
        
        # Elimina los archivos de la carpeta
        if os.path.exists(self.base_dir):
            for filename in os.listdir(self.base_dir):
                if filename.endswith(".pickle"):
                    file_path = os.path.join(self.base_dir, filename)
                    try:
                        os.remove(file_path)
                    except Exception as e:
                        print(f"Error al borrar archivo {file_path}: {e}")
        
        # Reinicia el estado interno del historial
        self.history = []
        self.current_history_index = -1
        self.time_instance = 0 # Reinicia el contador de tiempo
    

    # --- VARIABLES DE UNIDADES Y MAPA ---
    CELL_SIZE = 5 
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
    
    """
        CONSTRUCTOR DE LA CLASE MAPMANAGER
    """
    def __init__(self):

        self.entities = [] 
        self.mobile_mine = self.MOBILE_MINE_CLASS(id_=99)
        self.time_instance = 0
        self.mobile_mine_visible = False
        self.is_relocating = False
        self.vehicles = []
        # Inicializa la GRID MAESTRA para pathfinding (incluye bases y terreno)
        self.grid_maestra = self._crear_grid(self.GRID_FILAS_TOTALES, self.GRID_COLS_TOTALES)

        # RASTREO DE POSICIÓN ANTERIOR DE MINA MÓVIL
        self.old_mobile_mine_fila = -1
        self.old_mobile_mine_col = -1
        self._initial_placement_done = False # Bandera para la primera colocación

        # HISTORIAL Y PUNTERO PARA MANEJAR ESTADOS DE JUEGO
        self.history = [] 
        self.current_history_index = -1
        self.base_dir = "map_history" # Carpeta para guardar los estados
        
        # Atributos para los puntajes de los equipos
        self.puntajes = {'Rojo': 0, 'Azul': 0}
        self.recursos_restantes = 0


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
        
        if not (0 <= fila < self.GRID_FILAS_TOTALES and 0 <= col < self.GRID_COLS_TOTALES):
            return None, None # Fuera de límites

        entity_at_cell = self.grid_maestra[fila][col]

        if isinstance(entity_at_cell, Recurso):
            # Colisión con un Recurso
            # Si todavía tiene espacio para recoger recursos entra.
            if len(veh.recursos) < veh.viajesTotales:
                veh.recursos.append(entity_at_cell) 
                self.grid_maestra[fila][col] = 0  # elimina el recurso del mapa
                self.entities.remove(entity_at_cell)
                print(f"{veh.nombre} recogió un recurso ({entity_at_cell.tipo}).")
            return "recurso", entity_at_cell

        elif isinstance(entity_at_cell, vehicle) and entity_at_cell is not veh: 
            # Colisión con otro Vehículo (asegura que no sea el mismo vehículo)
            return "vehiculo", entity_at_cell
        
        all_mines = [e for e in self.entities if isinstance(e, Mina) and not e.movil]
        if self.mobile_mine_visible:
            all_mines.append(self.mobile_mine)
            
        for entity in all_mines:
            dist_col = abs(entity.columna - col)
            dist_fila = abs(entity.fila - fila)
            distance = math.sqrt(dist_col**2 + dist_fila**2)

            if entity.tipo in ["O1", "O2", "G1"]: # Minas Circulares
                if distance <= entity.radio:
                    # Colisión con una mina circular
                    return "mina_circular", entity

            elif entity.tipo == "T1": # Mina Horizontal (afecta por distancia en Y)
                if dist_fila <= entity.radio:
                    # Colisión con una mina horizontal
                    return "mina_horizontal", entity

            elif entity.tipo == "T2": # Mina Vertical (afecta por distancia en X)
                if dist_col <= entity.radio:
                    # Colisión con una mina vertical
                    return "mina_vertical", entity
                    
        
        # Si el vehículo llega a la base exitosamente, entregará los recursos que agarró.
        if veh.equipo == "Rojo" and self._en_base(veh, self.BASE1_GRID):
            self._entregar_recursos(veh)
        elif veh.equipo == "Azul" and self._en_base(veh, self.BASE2_GRID):
            self._entregar_recursos(veh)
        return None, None

# Función que devuelve True si el vehículo está en su base.
    def _en_base(self, vehiculo, base_zone):
        return (base_zone["min_col"] <= vehiculo.columna <= base_zone["max_col"]and base_zone["min_row"] <= vehiculo.fila <= base_zone["max_row"])

# Función que entrega todos los recursos recolectados y suma puntaje.
    def _entregar_recursos(self, vehiculo):
        if vehiculo.recursos:
            cantidad = len(vehiculo.recursos)
            puntos_ganados = sum(recurso.get_puntos() for recurso in vehiculo.recursos)  # obtiene el puntaje de cada recurso recolectado y los suma.
            self.puntajes[vehiculo.equipo] += puntos_ganados
            print(f"{vehiculo.nombre} entregó {cantidad} recursos (+{puntos_ganados} pts).")

            # Vacia el inventario.
            vehiculo.recursos.clear()

# Función para verificar las condiciones de parada de la simulación.
    def check_condiciones_parada(self):
        #**
        # Devuelve True cuando debe parar la simulación.
        # Cuando no haya más recursos disponibles, se detiene la simulación.
        # Cuando no hayan más vehículos en estado "activo" en un equipo, se detiene la simulación.
        # #
        
        # Revisa si quedan recursos disponibles 
        recursos_restantes = any(isinstance(e, Recurso) for e in self.entities)
        
        # Contar vehículos activos por equipo
        vehiculos_activos = {
            'Rojo': sum(1 for v in self.vehicles if v.equipo == "Rojo" and v.estado == "activo"),
            'Azul': sum(1 for v in self.vehicles if v.equipo == "Azul" and v.estado == "activo")
        }
        
        # Condiciones de parada
        if not recursos_restantes:
            print("[FIN] No quedan más recursos.")
            return True
        
        if vehiculos_activos['Rojo'] == 0:
            print("[FIN] Todos los vehículos del equipo Rojo están explotados.")
            return True
        
        if vehiculos_activos['Azul'] == 0:
            print("[FIN] Todos los vehículos del equipo Azul están explotados.")
            return True
        
        # Si ninguna condición se cumple, no se detiene la simulación.
        return False


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

        # Limpiamos el directorio y la lista que contiene los estados de la partida
        self._limpiar_historial()

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
                    self._marcar_area_mina(new_mine, valor=1)

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

    
    #esta funcion marca con unos el radio de explosion de las minas

    def _marcar_area_mina(self, mina: Mina, valor=1):
        fila_c, col_c = mina.fila, mina.columna
        radio = int(mina.radio) # Usamos el radio directamente para la grid

        filas, cols = self.GRID_FILAS_TOTALES, self.GRID_COLS_TOTALES

        #estas variables son para verificar que el radio no se vaya a salir del mapa, que daría index error
        #si quisieramos poner ahï un uno, de todas formas eso no debería pasar porque se supone que las minas 
        #spawnean bien, pero bueno... es, una lastima porque eso no anda bien
        max_fila = min(filas, fila_c + radio + 1)
        min_fila =  max(0, fila_c - radio)

        max_col = min(cols, col_c + radio + 1)
        min_col = max(0, col_c - radio)

        # Mina Circular (O1, O2, G1)
        if mina.tipo in ["O1", "O2", "G1"]:
            # Recorre un cuadrado que contiene el círculo de efecto
            for f in range(min_fila, max_fila):
                for c in range(min_col, max_col):
                    # Verifica si la celda (f, c) está dentro del radio
                    distance = math.sqrt((c - col_c)**2 + (f - fila_c)**2)
                    if distance <= radio:
                        self.grid_maestra[f][c] = valor
        
        # Mina Lineal Horizontal (T1)
        elif mina.tipo == "T1":
            
            for c in range(min_col, max_col + 1): 
                self.grid_maestra[mina.fila][c] = valor

        # Mina Lineal Vertical (T2)
        elif mina.tipo == "T2":

            for f in range(min_fila, max_fila + 1): 
                self.grid_maestra[f][mina.columna] = valor


    def _actualizar_grid_minas(self):
        """
        Actualiza la GRID MAESTRA SÓLO con la posición de la Mina G1
        sin regenerar toda la matriz.
        """
        
        # Borrar la posición anterior (solo si ya se colocó una vez)
        if self._initial_placement_done:
            """ Hay que hacer una nueva mina con las posiciones viejas, porque la funcion _marcar_area_mina usa los atributos
            fila y columna actuales, pero para borrar necesitamos las pòsiciones anteriores"""

            temp_mine_prev = self.MOBILE_MINE_CLASS(id_=99) # Tipo G1
            temp_mine_prev.set_posicion(self.old_mobile_mine_col, self.old_mobile_mine_fila)
            # Borrar el área de efecto con valor 0 (libre)
            self._marcar_area_mina(temp_mine_prev, valor=0)
            
            # Nota: Las minas estáticas deben haberse colocado una sola vez en distribute_entities.
            # Por eso esta función solo maneja la Mina G1.

        # Marcar la nueva posición si la mina está visible
        if self.mobile_mine_visible:
            # 1 = obstáculo/mina
            self._marcar_area_mina(self.mobile_mine, valor=1)
            
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

        # Guardamos el estado de juego despues de la logica del tick
        self.guardar_estado_historial()
        
        return self.time_instance