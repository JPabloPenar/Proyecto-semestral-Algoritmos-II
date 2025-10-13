import random
from mines import MinaO1, MinaO2, MinaT1, MinaT2, MinaG1, Mina
from resources import Persona, Ropa, Alimentos, Medicamentos, Armamentos, Recurso

class GameEngine:
    
    # --- Parámetros de Configuración Modificados ---
    
    # Nuevo margen de seguridad para que las entidades no se generen justo en el borde.
    BORDER_MARGIN = 20 
    
    # Ajustamos el área de generación para que sea más pequeña que el terreno visible.
    TERRAIN_CONFIG = {
        "min_x": 150 + BORDER_MARGIN, 
        "max_x": 650 - BORDER_MARGIN, 
        "min_y": 50 + BORDER_MARGIN, 
        "max_y": 400 - BORDER_MARGIN
    }
    
    # Clase de Mina Móvil y Estáticas (sin cambios)
    MINE_CLASSES = [MinaO1, MinaO2, MinaT1, MinaT2] 
    MOBILE_MINE_CLASS = MinaG1
    
    # Distribución de Recursos (sin cambios)
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
        """Genera una posición aleatoria dentro del Terreno de Acción con margen."""
        x = random.uniform(self.TERRAIN_CONFIG["min_x"], self.TERRAIN_CONFIG["max_x"])
        y = random.uniform(self.TERRAIN_CONFIG["min_y"], self.TERRAIN_CONFIG["max_y"])
        return x, y

    def _check_collision(self, x, y, new_entity):
        """
        Verifica si la posición (x, y) choca con el área de efecto o posición
        de una entidad estática existente (mina o recurso).
        """
        
        # Margen de seguridad aumentado para evitar colisiones entre minas
        SAFETY_MARGIN = 15 

        for entity in self.entities:
            
            # --- 1. Chequeo de colisión entre MINAS y nuevas entidades ---
            if isinstance(entity, Mina):
                
                # Colisión Mina ESTÁTICA vs. Nueva Entidad
                
                
                # Minas Circulares (O1, O2)
                if entity.tipo in ["O1", "O2"]:
                    distance = ((entity.x - x)**2 + (entity.y - y)**2)**0.5
                    # La distancia de separación debe ser mayor al radio de efecto de la mina, más un margen
                    if distance < entity.radio + SAFETY_MARGIN: 
                        return True

                # Mina T1 (Horizontal)
                elif entity.tipo == "T1":
                    # Colisión si la nueva entidad cae dentro de la franja vertical de la mina
                    if abs(entity.y - y) < entity.radio + SAFETY_MARGIN:
                        return True
                        
                # Mina T2 (Vertical)
                elif entity.tipo == "T2":
                    # Colisión si la nueva entidad cae dentro de la franja horizontal de la mina
                    if abs(entity.x - x) < entity.radio + SAFETY_MARGIN:
                        return True
                    
            # --- 2. Chequeo de colisión entre RECURSOS ---
            # Solo si la entidad nueva es un Recurso, verificamos colisión con Recursos existentes
            if isinstance(new_entity, Recurso) and isinstance(entity, Recurso):
                distance = ((entity.x - x)**2 + (entity.y - y)**2)**0.5
                if distance < 5: # Margen pequeño para evitar apilamiento
                    return True
                         
        return False

    def _relocate_mobile_mine(self):
            """
            Reubica la Mina G1 de forma segura (sin colisionar con entidades estáticas).
            Esta función se llama cuando la mina está invisible (transición instantánea).
            """
            print("Reubicando Mina G1...")
            placed = False
            attempts = 0
            # Usamos el objeto MinaG1 existente en el chequeo de colisión
            new_mine = self.mobile_mine
            
            while not placed and attempts < 1000:
                x, y = self._get_random_pos()
                
                # Chequeamos colisión contra todas las entidades estáticas
                if not self._check_collision(x, y, new_mine): 
                    self.mobile_mine.set_posicion(x, y)
                    placed = True
                attempts += 1
            
            if not placed:
                print("ADVERTENCIA: No se pudo colocar Mina G1 sin colisión. Colocada aleatoriamente.")
                x, y = self._get_random_pos()
                self.mobile_mine.set_posicion(x, y)

    def distribute_entities(self):
        # ... (el resto de la función distribute_entities no necesita cambios)
        print("--- Iniciando Distribución Aleatoria (Init) ---")
        self.entities = []
        entity_id_counter = 1
        
        # 1. Distribuir Minas Estáticas (aumentamos intentos por mayor restricción de espacio)
        for MineClass in self.MINE_CLASSES:
            placed = False
            attempts = 0
            while not placed and attempts < 5000: # Aumentamos intentos a 5000
                x, y = self._get_random_pos()
                new_mine = MineClass(id_=entity_id_counter)
                if not self._check_collision(x, y, new_mine):
                    new_mine.set_posicion(x, y)
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
                    x, y = self._get_random_pos()
                    new_resource = ResourceClass(id_=entity_id_counter)
                    if not self._check_collision(x, y, new_resource):
                        new_resource.set_posicion(x, y)
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
        print(f"Distribución finalizada. Entidades estáticas: {len(self.entities)}")

    RELOCATION_TICK = 100
    def update_time(self):
        self.time_instance += 1
        
        # Lógica de Mina G1: aparece y desaparece cada 5 instancias de tiempo
        if self.is_relocating:
            # Pasa 1 tick invisible (instantáneo)
            self._relocate_mobile_mine()
            self.mobile_mine_visible = True
            self.is_relocating = False
            print(f"G1 reaparece en: ({int(self.mobile_mine.x)}, {int(self.mobile_mine.y)})")
            
        elif self.time_instance % self.RELOCATION_TICK == 0:
            # Tick donde debe moverse (Pasa 1 tick visible -> 1 tick invisible)
            self.mobile_mine_visible = False
            self.is_relocating = True
            print(f"G1 desaparece en el tick {self.time_instance}.")
        
        return self.time_instance