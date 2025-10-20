import pygame
import sys
import os
from map_manager import MapManager 
from mines import Mina, MinaT1, MinaT2, MinaG1
from resources import Recurso, Persona
from vehicles import jeep, moto, camion, auto

# --- Configuración y Constantes ---
pygame.init()

# Definición de Colores (RGB)
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
ROSA_CLARO = (255, 220, 230)
VERDE_INIT = (173, 255, 173)
AMARILLO_PLAY = (255, 255, 153)
GRIS_STOP = (200, 200, 200)
GRIS_OSCURO_BOTONES = (180, 180, 180)
TERRENO_FONDO = (250, 250, 250)

# Colores para representar entidades
COLOR_MINA_CIRCULAR = (100, 100, 100)
COLOR_MINA_LINEAL = (150, 0, 0)       
COLOR_MINA_MOVIL = (255, 140, 0)      
COLOR_PERSONA = (0, 0, 200)           
COLOR_RECURSO = (0, 200, 0)           

# Colores para representar equipos
COLOR_ROJO_EQUIPO = (255, 0, 0) # Rojo para Equipo "Rojo"
COLOR_AZUL_EQUIPO = (0, 0, 255) # Azul para Equipo "Azul"

# Dimensiones de la Ventana
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
VENTANA_TAMANIO = (ANCHO_VENTANA, ALTO_VENTANA)

# Creación de la Ventana
ventana = pygame.display.set_mode(VENTANA_TAMANIO)
pygame.display.set_caption("Simulador de Rescate")

# Reloj y estado de la simulación
reloj = pygame.time.Clock()
SIMULATION_FPS = 60 # 60 ticks por segundo
SIMULATION_STATE = "STOPPED" # STOPPED, INITIALIZED, PLAYING

# --- Rectángulos y Botones ---
ANCHO_BASE = 150
ALTO_BASE = 350
ANCHO_TERRENO = ANCHO_VENTANA - (2 * ANCHO_BASE)
ALTO_TERRENO = ALTO_BASE
MARGEN_SUPERIOR = 50
ESPACIO_CENTRAL = 50 

# 3 Rectangulos principales del juego
rect_base1 = pygame.Rect(0, MARGEN_SUPERIOR, ANCHO_BASE, ALTO_BASE)
rect_terreno = pygame.Rect(ANCHO_BASE, MARGEN_SUPERIOR, ANCHO_TERRENO, ALTO_TERRENO)
rect_base2 = pygame.Rect(ANCHO_BASE + ANCHO_TERRENO, MARGEN_SUPERIOR, ANCHO_BASE, ALTO_BASE)

# Definimos y otorgamos variables para los botones
ALTO_BOTON = 50
ANCHO_BOTON = 100
MARGEN_HORIZONTAL_BOTONES = 20
MARGEN_VERTICAL_BOTONES = rect_terreno.bottom + ESPACIO_CENTRAL

x_centro_terreno = rect_terreno.left + ANCHO_TERRENO / 2
x_init = x_centro_terreno - 2.5 * ANCHO_BOTON - 2 * MARGEN_HORIZONTAL_BOTONES
x_prev = x_centro_terreno - 1.5 * ANCHO_BOTON - MARGEN_HORIZONTAL_BOTONES
x_play = x_centro_terreno - 0.5 * ANCHO_BOTON
x_next = x_centro_terreno + 0.5 * ANCHO_BOTON + MARGEN_HORIZONTAL_BOTONES
x_stop = x_centro_terreno + 1.5 * ANCHO_BOTON + 2 * MARGEN_HORIZONTAL_BOTONES

rect_init = pygame.Rect(x_init, MARGEN_VERTICAL_BOTONES, ANCHO_BOTON, ALTO_BOTON)
rect_prev = pygame.Rect(x_prev, MARGEN_VERTICAL_BOTONES, ANCHO_BOTON, ALTO_BOTON)
rect_play = pygame.Rect(x_play, MARGEN_VERTICAL_BOTONES, ANCHO_BOTON, ALTO_BOTON)
rect_next = pygame.Rect(x_next, MARGEN_VERTICAL_BOTONES, ANCHO_BOTON, ALTO_BOTON)
rect_stop = pygame.Rect(x_stop, MARGEN_VERTICAL_BOTONES, ANCHO_BOTON, ALTO_BOTON)

botones = {
    "Init": {"rect": rect_init, "message": "Distribución Aleatoria."},
    "<<": {"rect": rect_prev, "message": "Replay: Retroceso."},
    "Play": {"rect": rect_play, "message": "Simulación en curso..."},
    ">>": {"rect": rect_next, "message": "Replay: Avance."},
    "Stop": {"rect": rect_stop, "message": "Deteniendo simulación."}
}

# --- Fuentes ---
fuente_titulo = pygame.font.Font(None, 24)
fuente_boton = pygame.font.Font(None, 30)


# --- Funciones de Dibujo ---
def draw_vehicle(surface, vehicle_type, color, x, y):
    """Dibuja una representación de un vehículo."""
    
    VEHICLE_WIDTH = 20 
    VEHICLE_HEIGHT = 12
    WHEEL_RADIUS = 3
    
    if vehicle_type == "Jeep":
        # Rectángulo (cuerpo)
        pygame.draw.rect(surface, color, (x, y, VEHICLE_WIDTH, VEHICLE_HEIGHT), border_radius=3)
        # Ruedas
        pygame.draw.circle(surface, NEGRO, (x + 5, y + VEHICLE_HEIGHT), WHEEL_RADIUS)
        pygame.draw.circle(surface, NEGRO, (x + VEHICLE_WIDTH - 5, y + VEHICLE_HEIGHT), WHEEL_RADIUS)
        
    elif vehicle_type == "Moto":
        # Cuerpo delgado y ruedas más pequeñas
        pygame.draw.line(surface, color, (x, y + 8), (x + VEHICLE_WIDTH - 5, y + 8), 4)
        pygame.draw.circle(surface, NEGRO, (x + 4, y + 12), WHEEL_RADIUS)
        pygame.draw.circle(surface, NEGRO, (x + VEHICLE_WIDTH - 8, y + 12), WHEEL_RADIUS)
        
    elif vehicle_type == "Camion":
        # Rectángulo más largo y alto (camión)
        TRUCK_WIDTH = 30
        TRUCK_HEIGHT = 15
        pygame.draw.rect(surface, color, (x, y, TRUCK_WIDTH, TRUCK_HEIGHT), border_radius=4)
        # Ruedas
        pygame.draw.circle(surface, NEGRO, (x + 8, y + TRUCK_HEIGHT), WHEEL_RADIUS + 1)
        pygame.draw.circle(surface, NEGRO, (x + TRUCK_WIDTH - 8, y + TRUCK_HEIGHT), WHEEL_RADIUS + 1)
        
    elif vehicle_type == "Auto":
        # Rectángulo más plano y bajo
        CAR_HEIGHT = 15
        pygame.draw.rect(surface, color, (x, y + 3, VEHICLE_WIDTH - 5, CAR_HEIGHT), border_radius=3)
        # Ruedas
        pygame.draw.circle(surface, NEGRO, (x + 5, y + CAR_HEIGHT + 3), WHEEL_RADIUS)
        pygame.draw.circle(surface, NEGRO, (x + VEHICLE_WIDTH - 10, y + CAR_HEIGHT + 3), WHEEL_RADIUS)

def inicializar_equipos(rect_base1, rect_base2):
    """Crea objetos de vehículo y les asigna posiciones de inicio distribuidas dentro de su base."""

    clases_vehiculos = [
        jeep, jeep, jeep, # 3 Jeeps
        moto, moto, # 2 Motos
        camion, camion, # 2 Camiones
        auto, auto, auto # 3 Autos
    ]
    
    START_X_OFFSET = 60 # Desplazamiento horizontal desde el borde izquierdo
    START_Y_OFFSET = 20 # Desplazamiento vertical inicial
    SPACING = 30        # Espacio vertical entre vehículos
    
    flota_1 = []
    # Base 1 (equipo rojo):
    for i, Clase in enumerate(clases_vehiculos): 
        # Calcula la posición de inicio para que se vea ordenado en la base
        pos_x1 = rect_base1.left + START_X_OFFSET
        pos_y1 = rect_base1.top + START_Y_OFFSET + i * SPACING 
        
        veh = Clase(columna=pos_x1 // 5,
                     fila=pos_y1 // 5, 
                     equipo="Rojo"
                     )
        
        flota_1.append(veh)

    
    flota_2 = []
    # Base 2 (equipo azul):
    for i, Clase in enumerate(clases_vehiculos):
        # Calcula la posición de inicio para que se vea ordenado en la base
        pos_x2 = rect_base2.left + START_X_OFFSET
        pos_y2 = rect_base2.top + START_Y_OFFSET + i * SPACING
        
        veh = Clase( # constructor
            columna=pos_x2 // 5, 
            fila=pos_y2 // 5, 
            equipo="Azul"
        )
        
        flota_2.append(veh)

    return flota_1, flota_2

# Inicializar las flotas con los vehículos creados
flota_base1, flota_base2 = inicializar_equipos(rect_base1, rect_base2)
flota_total = flota_base1 + flota_base2

def draw_entities(surface, engine):
    """Dibuja las minas y recursos en el Terreno de Acción."""
    
    # --- Dibujo de Recursos ---
    for entity in engine.entities:
        if isinstance(entity, Recurso):
            x, y = entity.columna * 5, entity.fila * 5
            color = COLOR_PERSONA if isinstance(entity, Persona) else COLOR_RECURSO
            
            if isinstance(entity, Persona):
                pygame.draw.circle(surface, color, (int(x), int(y)), 2.5)
            else:
                pygame.draw.rect(surface, color, (int(x) - 2.5, int(y) - 2.5, 5, 5))

    # 2. Dibujar Minas Estáticas
    for entity in engine.entities:
        if isinstance(entity, Mina) and not entity.movil:
            x, y = entity.columna * 5, entity.fila * 5
            radio = entity.radio # Radio de efecto (no de dibujo)
            
            # NUEVO TAMAÑO VISUAL DE LAS MINAS
            VISUAL_SIZE = 40
            
            if isinstance(entity, MinaT1): # Horizontal (Mina T1)
                # Dibuja línea central más grande
                pygame.draw.line(surface, COLOR_MINA_LINEAL, (x - VISUAL_SIZE, y), (x + VISUAL_SIZE, y), 4)
                
                
            elif isinstance(entity, MinaT2): # Vertical (Mina T2)
                # Dibuja línea central más grande
                pygame.draw.line(surface, COLOR_MINA_LINEAL, (x, y - VISUAL_SIZE), (x, y + VISUAL_SIZE), 4)

                
            else: # Circular (Mina O1, O2)
                # Dibuja el radio de efecto
                pygame.draw.circle(surface, COLOR_MINA_CIRCULAR, (x, y), int(radio)*5, 2) # Borde del área de efecto
                # Dibuja el cuerpo de la mina
                pygame.draw.circle(surface, NEGRO, (x, y), 5) 

    # 3. Dibujar Mina G1
    if engine.mobile_mine and engine.mobile_mine_visible:
        x, y = int(engine.mobile_mine.columna) * 5, int(engine.mobile_mine.fila) * 5
        radio = engine.mobile_mine.radio
        
        # Dibujar el radio de efecto
        pygame.draw.circle(surface, COLOR_MINA_MOVIL, (x, y), int(radio)*5, 2)
        
        # Dibujar el cuerpo de la mina (Cuadrado/Diamante)
        size = 1
        puntos = [
            (x, y - size), # Arriba
            (x + size, y), # Derecha
            (x, y + size), # Abajo
            (x - size, y)  # Izquierda
        ]
        pygame.draw.polygon(surface, COLOR_MINA_MOVIL, puntos)
        pygame.draw.polygon(surface, NEGRO, puntos, 1) # Borde negro

# --- INICIALIZACION DEL MOTOR DE JUEGO ---
ENGINE_HISTORY_FILE = "map_history/state_0000.pickle"

# Intenta cargar el estado inicial. Si falla o no existe, devuelve None.
engine = MapManager.cargar_estado(ENGINE_HISTORY_FILE)

# Si engine es None, significa que no se pudo cargar o no existía el archivo.
if engine is None: 
    engine = MapManager()

# --- BUCLE PRINCIPAL DEL JUEGO (GAME LOOP) ---
def main_loop():
    global SIMULATION_STATE, engine
    ejecutando = True
    
    engine.distribute_entities() # Inicialización forzada de minas/recursos al inicio
    engine.current_history_index = 0 # Inicializacion del puntero
    SIMULATION_STATE = "INITIALIZED"
    
    while ejecutando:
        
        # 1. Procesamiento de Eventos
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            
            if evento.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = evento.pos
                
                # --- Lógica de Botones ---
                if botones["Init"]["rect"].collidepoint(mouse_pos):
                    # BOTÓN INIT: Distribuye minass y recursos si no está corriendo
                    if SIMULATION_STATE != "PLAYING":
                        engine.distribute_entities()
                        SIMULATION_STATE = "INITIALIZED"
                        print(f"[INITIALIZED] Nueva distribución generada.")
                    else:
                        print("La simulación debe estar detenida para reinicializar.")
                        
                elif botones["Play"]["rect"].collidepoint(mouse_pos):
                    # BOTÓN PLAY
                    if SIMULATION_STATE == "INITIALIZED" or SIMULATION_STATE == "STOPPED":
                        SIMULATION_STATE = "PLAYING"

                        # for veh in flota_total:
                        #     veh.agragarobjetivo(300,300)
                        #     veh.calcular_camino
                        print(f"[PLAYING] Simulación Iniciada (Time Instance: {engine.time_instance}).")

                elif botones["Stop"]["rect"].collidepoint(mouse_pos):
                    # BOTÓN STOP
                    if SIMULATION_STATE == "PLAYING":
                        SIMULATION_STATE = "STOPPED"
                        print(f"[STOPPED] Simulación Detenida.")
                    
                # << y >> (Mensajes)
                elif botones["<<"]["rect"].collidepoint(mouse_pos):

                    # Si estamos jugando
                    if SIMULATION_STATE == "PLAYING":
                        print("La simulación debe estar detenida para retroceder.")
                    
                    # Si no estamos jugando y hay eventos anteriores
                    elif SIMULATION_STATE == "STOPPED" and engine.current_history_index > 0:
                        engine.current_history_index -= 1
                        # Carga el estado anterior y reemplaza el objeto 'engine' actual
                        new_engine = MapManager.cargar_estado(engine.history[engine.current_history_index])
                        if new_engine:
                            engine = new_engine # Reemplaza el motor por el estado anterior
                            print(f"[REPLAY] Retroceso a Time Instance: {engine.time_instance}")


                    # Si estamos al principio de la simulacion (no hay eventos anteriores)
                    elif engine.current_history_index == 0:
                        print("Ya estás en el inicio de la simulación.")

                elif botones[">>"]["rect"].collidepoint(mouse_pos):

                    if SIMULATION_STATE == "PLAYING":
                        print("La simulación debe estar detenida para avanzar en el replay.")

                    # ¿Hay un estado futuro grabado (en el historial) al que avanzar?
                    elif engine.current_history_index < len(engine.history) - 1:
                        engine.current_history_index += 1
                        # Carga el estado siguiente y reemplaza el objeto 'engine' actual
                        new_engine = MapManager.cargar_estado(engine.history[engine.current_history_index])
                        if new_engine:
                            engine = new_engine
                            print(f"[REPLAY] Avance a Time Instance: {engine.time_instance}.")
                            
                    else:
                        engine.update_time() # Guarda el nuevo estado, incrementa time_instance y history_index
                        
                        # Lógica del vehículo (copiada del SIMULATION_STATE == "PLAYING" original)
                        for veh in flota_total:
                            if veh.camino:
                                veh.mover_por_camino()
                            veh.actualizar_objetivo(engine.grid_maestra)
                            
                            if veh.estado == "activo":
                                collision_type, entity = engine.check_vehicle_collisions(veh)
                                
                                # Lógica simplificada de colisión (Mina/Recurso) para el tick único
                                if collision_type and entity:
                                    if collision_type.startswith("mina"):
                                        veh.explotar()
                                        veh.camino = []
                                        print(f"¡Explosión! {veh.__class__.__name__} (Time: {engine.time_instance})")
                                    elif collision_type == "recurso":
                                        if veh.viajesActuales > 0:
                                            veh.recoger()
                                            print(f"({veh.equipo}) recogió Recurso ({entity.__class__.__name__}) en ({veh.columna}, {veh.fila}) (Time: {engine.time_instance}).")
                                            engine.grid_maestra[veh.fila][veh.columna] = 0
                                            engine.entities.remove(entity)
                                        else:
                                            print(f"{veh.__class__.__name__} ({veh.equipo}) no puede llevar más carga (Capacidad llena).")
                                    
                                    elif collision_type == "vehiculo":
                                        veh.explotar()
                                        veh.camino = [] # Detiene el movimiento
                                        entity.explotar()
                                        entity.camino = []
                                        print(f"Choque de {veh.__class__.__name__} y {entity.__class__.__name__}")
                                            
                        SIMULATION_STATE = "STOPPED"
                        print(f"[TICK] Avanzado un paso (Time Instance: {engine.time_instance}).")


        # 2. Lógica de Actualización (Tick del juego)
        if SIMULATION_STATE == "PLAYING":
            # Avanza la instancia de tiempo. Maneja la aparición/desaparición de Mina G1.
            engine.update_time()

            for veh in flota_total:
                """
                En esta parte nos encargamos de verificar las colisiones de los vehiculos
                Se imprimen mensajes por pantalla de ser necesario.
                TODO:
                    Se deben sacar los objetos con los que colisiono del mapa (minas explotadas y recursos recogidos)
                """
                if veh.camino:
                    veh.mover_por_camino()

                veh.actualizar_objetivo(engine.grid_maestra)

                if veh.estado == "activo":
                    
                    collision_type, entity = engine.check_vehicle_collisions(veh)
                    
                    if collision_type and entity:
                        
                        if collision_type.startswith("mina"):
                            # El vehículo explota y se desactiva
                            veh.explotar()
                            veh.camino = [] # Detiene el movimiento
                            print(f"¡Explosión! {veh.__class__.__name__}")
                            
                            # Si el auto colisiona podriamos quitar la mina de la colision
                            # TODO: consultar acerca de esto

                        elif collision_type == "recurso":
                            # El vehículo recoge el recurso si su capacidad se lo permite
                            if veh.carga == entity.tipoDeCarga or veh.carga == "todo":
                                # Solo recoge si tiene viajes disponibles
                                if veh.viajesActuales > 0:
                                    veh.recoger() # Disminuye viajesActuales
                                    print(f"({veh.equipo}) recogió Recurso ({entity.__class__.__name__}) en ({veh.columna}, {veh.fila}).")
                                    
                                    # Quitar el recurso de la grid y de la lista de entidades
                                    engine.grid_maestra[veh.fila][veh.columna] = 0 # Deja la celda libre
                                    engine.entities.remove(entity)
                                else:
                                    print(f"{veh.__class__.__name__} ({veh.equipo}) no puede llevar más carga (Capacidad llena).")
                        
                        elif collision_type == "vehiculo":
                            #TODO: CHEQUEAR
                            veh.explotar()
                            veh.camino = [] # Detiene el movimiento
                            entity.explotar()
                            entity.camino = []
                            print(f"Choque de {veh.__class__.__name__} y {entity.__class__.__name__}")
                                                                

        # 3. Dibujo
        ventana.fill(BLANCO)

        # Dibujar Bases y Terreno
        pygame.draw.rect(ventana, ROSA_CLARO, rect_base1, border_radius=10)
        pygame.draw.rect(ventana, NEGRO, rect_base1, 2, border_radius=10)
        pygame.draw.rect(ventana, ROSA_CLARO, rect_base2, border_radius=10)
        pygame.draw.rect(ventana, NEGRO, rect_base2, 2, border_radius=10)
        pygame.draw.rect(ventana, TERRENO_FONDO, rect_terreno, border_radius=10)
        pygame.draw.rect(ventana, ROSA_CLARO, rect_terreno, 4, border_radius=10)

        # Dibujar Títulos
        texto_base1 = fuente_titulo.render("Base 1", True, NEGRO)
        texto_terreno = fuente_titulo.render("Terreno de Accion (Time: {})".format(engine.time_instance), True, NEGRO)
        texto_base2 = fuente_titulo.render("Base 2", True, NEGRO)

        ventana.blit(texto_base1, (rect_base1.centerx - texto_base1.get_width() // 2, rect_base1.top - 20))
        ventana.blit(texto_terreno, (rect_terreno.centerx - texto_terreno.get_width() // 2, rect_terreno.top - 20))
        ventana.blit(texto_base2, (rect_base2.centerx - texto_base2.get_width() // 2, rect_base2.top - 20))

        # Dibujar Entidades (Recursos y Minas)
        draw_entities(ventana, engine)
        
        for veh in flota_total:
            if veh.equipo == "Rojo":
                color = COLOR_ROJO_EQUIPO
            elif veh.equipo == "Azul":
                color = COLOR_AZUL_EQUIPO
            else:
                color = NEGRO 
            vehicle_type = veh.__class__.__name__.capitalize() 
            draw_vehicle(ventana, vehicle_type, color, veh.columna * 5, veh.fila * 5)

        # Dibujar Botones
        for name, data in botones.items():
            rect = data["rect"]
            color = VERDE_INIT if name == "Init" else AMARILLO_PLAY if name == "Play" else GRIS_STOP if name == "Stop" else GRIS_OSCURO_BOTONES
                
            pygame.draw.rect(ventana, color, rect, border_radius=5)
            pygame.draw.rect(ventana, NEGRO, rect, 2, border_radius=5)
            
            texto_boton = fuente_boton.render(name, True, NEGRO)
            ventana.blit(texto_boton, (rect.centerx - texto_boton.get_width() // 2, rect.centery - texto_boton.get_height() // 2))

        # 4. Actualizar la Pantalla
        pygame.display.flip()
        reloj.tick(SIMULATION_FPS)

    # --- FINALIZACIÓN ---
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main_loop()