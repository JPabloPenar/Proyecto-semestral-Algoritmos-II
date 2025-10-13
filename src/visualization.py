import pygame
import sys
import os
# Asegúrate de que estos imports funcionen (los archivos deben estar en la misma carpeta)
from game_engine import GameEngine 
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

# --- Rectángulos y Botones (Mismos que el código anterior) ---
ANCHO_BASE = 150
ALTO_BASE = 350
ANCHO_TERRENO = ANCHO_VENTANA - (2 * ANCHO_BASE)
ALTO_TERRENO = ALTO_BASE
MARGEN_SUPERIOR = 50
ESPACIO_CENTRAL = 50 

rect_base1 = pygame.Rect(0, MARGEN_SUPERIOR, ANCHO_BASE, ALTO_BASE)
rect_terreno = pygame.Rect(ANCHO_BASE, MARGEN_SUPERIOR, ANCHO_TERRENO, ALTO_TERRENO)
rect_base2 = pygame.Rect(ANCHO_BASE + ANCHO_TERRENO, MARGEN_SUPERIOR, ANCHO_BASE, ALTO_BASE)

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

# --- Inicialización del Motor del Juego ---
engine = GameEngine()

# --- Fuentes ---
fuente_titulo = pygame.font.Font(None, 24)
fuente_boton = pygame.font.Font(None, 30)

# --- Funciones de Dibujo ---

def draw_vehicle(surface, vehicle_type, color, x, y):
    """Dibuja una representación de un vehículo."""
    
    # NUEVAS DIMENSIONES
    VEHICLE_WIDTH = 30 
    VEHICLE_HEIGHT = 18
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
        TRUCK_WIDTH = 40
        TRUCK_HEIGHT = 20
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


def draw_fleet_at_base(surface, fleet_list, base_rect):
    """Dibuja los vehículos en la base."""
    
    start_x = base_rect.left +60
    start_y = base_rect.top + 20
    # Espacio vertical reducido
    spacing = 30 

    for i, veh in enumerate(fleet_list):
        y_pos = start_y + i * spacing
        
        # Determinar el color basado en el equipo
        if veh.equipo == "Rojo":
            color = COLOR_ROJO_EQUIPO
        elif veh.equipo == "Azul":
            color = COLOR_AZUL_EQUIPO
        else:
            color = NEGRO # Color por defecto

        # El tipo de vehículo se deduce de su clase
        vehicle_type = veh.__class__.__name__.capitalize() 

        draw_vehicle(surface, vehicle_type, color, start_x, y_pos)

def inicializar_equipos(rect_base1, rect_base2, ancho_terreno):
    """Crea objetos de vehículo y los asigna las bases correspondientes"""

    clases_vehiculos = [
        jeep, jeep, jeep,  # 3 Jeeps
        moto, moto,        # 2 Motos
        camion, camion,    # 2 Camiones
        auto, auto, auto   # 3 Autos
    ]
    
    pos_x1 = rect_base1.centerx
    pos_y1 = rect_base1.centery
    
    flota_1 = []
    # base 1(equipo rojo):
    for Clase in clases_vehiculos: # El constructor en vehicles.py no recibe 'viajesActuales' ni 'estado'
        veh = Clase( #constructor
            posicionX=pos_x1, 
            posicionY=pos_y1, 
            equipo="Rojo"
        )
        
        
        flota_1.append(veh)

    
    pos_x2 = rect_base2.centerx
    pos_y2 = rect_base2.centery

    flota_2 = []
    # base 2(equipo azul):
    for Clase in clases_vehiculos:
        veh = Clase( #constructor
            posicionX=pos_x2, 
            posicionY=pos_y2, 
            equipo="Azul"
        )
        
        flota_2.append(veh)

    return flota_1, flota_2

# Inicializar las flotas con los vehículos creados
flota_base1, flota_base2 = inicializar_equipos(rect_base1, rect_base2, ANCHO_TERRENO)

def draw_entities(surface, engine):
    """Dibuja las minas y recursos en el Terreno de Acción."""
    
    # ... (Dibujo de Recursos - sin cambios)
    for entity in engine.entities:
        if isinstance(entity, Recurso):
            color = COLOR_PERSONA if isinstance(entity, Persona) else COLOR_RECURSO
            
            if isinstance(entity, Persona):
                pygame.draw.circle(surface, color, (int(entity.x), int(entity.y)), 4)
            else:
                pygame.draw.rect(surface, color, (int(entity.x) - 3, int(entity.y) - 3, 6, 6))

    # 2. Dibujar Minas Estáticas
    for entity in engine.entities:
        if isinstance(entity, Mina) and not entity.movil:
            x, y = int(entity.x), int(entity.y)
            radio = entity.radio # Radio de efecto (no de dibujo)
            
            # NUEVO TAMAÑO VISUAL DE LAS MINAS
            VISUAL_SIZE = 40 
            
            if isinstance(entity, MinaT1): # Horizontal (Mina T1)
                # Dibuja línea central más grande
                pygame.draw.line(surface, COLOR_MINA_LINEAL, (x - VISUAL_SIZE, y), (x + VISUAL_SIZE, y), 4)
                # Dibuja límites de radio de efecto (área peligrosa)
                pygame.draw.line(surface, (150, 50, 50), (x - VISUAL_SIZE, y - radio), (x + VISUAL_SIZE, y - radio), 1)
                pygame.draw.line(surface, (150, 50, 50), (x - VISUAL_SIZE, y + radio), (x + VISUAL_SIZE, y + radio), 1)
                
            elif isinstance(entity, MinaT2): # Vertical (Mina T2)
                # Dibuja línea central más grande
                pygame.draw.line(surface, COLOR_MINA_LINEAL, (x, y - VISUAL_SIZE), (x, y + VISUAL_SIZE), 4)
                # Dibuja límites de radio de efecto (área peligrosa)
                pygame.draw.line(surface, (150, 50, 50), (x - radio, y - VISUAL_SIZE), (x - radio, y + VISUAL_SIZE), 1)
                pygame.draw.line(surface, (150, 50, 50), (x + radio, y - VISUAL_SIZE), (x + radio, y + VISUAL_SIZE), 1)
                
            else: # Circular (Mina O1, O2)
                # Dibuja el radio de efecto
                pygame.draw.circle(surface, COLOR_MINA_CIRCULAR, (x, y), int(radio), 2) # Borde del área de efecto
                # Dibuja el cuerpo de la mina
                pygame.draw.circle(surface, NEGRO, (x, y), 5) 

    # 3. Dibujar Mina G1 (Móvil - CAMBIO EN DIBUJO)
    if engine.mobile_mine and engine.mobile_mine_visible:
        x, y = int(engine.mobile_mine.x), int(engine.mobile_mine.y)
        radio = engine.mobile_mine.radio
        
        # Dibujar el radio de efecto (Círculo Naranja)
        pygame.draw.circle(surface, COLOR_MINA_MOVIL, (x, y), int(radio), 2)
        
        # Dibujar el cuerpo de la mina (Cuadrado/Diamante)
        size = 8
        puntos = [
            (x, y - size), # Arriba
            (x + size, y), # Derecha
            (x, y + size), # Abajo
            (x - size, y)  # Izquierda
        ]
        pygame.draw.polygon(surface, COLOR_MINA_MOVIL, puntos)
        pygame.draw.polygon(surface, NEGRO, puntos, 1) # Borde negro


# --- BUCLE PRINCIPAL DEL JUEGO (GAME LOOP) ---
def main_loop():
    global SIMULATION_STATE
    ejecutando = True
    
    # Inicialización forzada de minas/recursos al inicio (Init inicial)
    engine.distribute_entities()
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
                        print(f"[PLAYING] Simulación Iniciada (Time Instance: {engine.time_instance}).")

                elif botones["Stop"]["rect"].collidepoint(mouse_pos):
                    # BOTÓN STOP
                    if SIMULATION_STATE == "PLAYING":
                        SIMULATION_STATE = "STOPPED"
                        print(f"[STOPPED] Simulación Detenida.")
                    
                # << y >> (Mensajes)
                elif botones["<<"]["rect"].collidepoint(mouse_pos):
                    print(f"[{SIMULATION_STATE}] {botones['<<']['message']}")
                elif botones[">>"]["rect"].collidepoint(mouse_pos):
                    print(f"[{SIMULATION_STATE}] {botones['>>']['message']}")

        # 2. Lógica de Actualización (Tick del juego)
        if SIMULATION_STATE == "PLAYING":
            # Avanza la instancia de tiempo. Maneja la aparición/desaparición de Mina G1.
            engine.update_time()

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
        
        # C. Dibujar la Flota de Vehículos en ambas bases
        draw_fleet_at_base(ventana, flota_base1, rect_base1)
        draw_fleet_at_base(ventana, flota_base2, rect_base2)
        
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