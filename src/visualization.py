import pygame
import sys


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

# Colores para representar los vehículos
COLOR_JEEP = (0, 100, 0)      # Verde oscuro
COLOR_MOTO = (255, 165, 0)    # Naranja
COLOR_TRUCK = (255, 0, 0)     # Rojo
COLOR_CAR = (0, 0, 255)       # Azul

# Dimensiones de la Ventana
ANCHO_VENTANA = 800
ALTO_VENTANA = 600
VENTANA_TAMANIO = (ANCHO_VENTANA, ALTO_VENTANA)

# Creación de la Ventana
ventana = pygame.display.set_mode(VENTANA_TAMANIO)
pygame.display.set_caption("Simulador de Rescate - Interfaz")

# Reloj para controlar la velocidad del juego
reloj = pygame.time.Clock()

# --- Rectángulos de la Interfaz ---
ANCHO_BASE = 150
ALTO_BASE = 350
ANCHO_TERRENO = ANCHO_VENTANA - (2 * ANCHO_BASE)
ALTO_TERRENO = ALTO_BASE
MARGEN_SUPERIOR = 50
ESPACIO_CENTRAL = 50 

# Rectángulos principales (Base, Terreno, Base)
rect_base1 = pygame.Rect(0, MARGEN_SUPERIOR, ANCHO_BASE, ALTO_BASE)
rect_terreno = pygame.Rect(ANCHO_BASE, MARGEN_SUPERIOR, ANCHO_TERRENO, ALTO_TERRENO)
rect_base2 = pygame.Rect(ANCHO_BASE + ANCHO_TERRENO, MARGEN_SUPERIOR, ANCHO_BASE, ALTO_BASE)

# Rectángulos de los botones
ALTO_BOTON = 50
ANCHO_BOTON = 100
MARGEN_HORIZONTAL_BOTONES = 20
MARGEN_VERTICAL_BOTONES = rect_terreno.bottom + ESPACIO_CENTRAL

# Posiciones centradas para los botones
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

# Diccionario de botones para manejo de clics
botones = {
    "Init": {"rect": rect_init, "message": "Inicializando el mapa: Distribución Aleatoria."},
    "<<": {"rect": rect_prev, "message": "Modo Replay: Retroceso de un paso."},
    "Play": {"rect": rect_play, "message": "Iniciando/Reanudando la Simulación."},
    ">>": {"rect": rect_next, "message": "Modo Replay: Avance de un paso."},
    "Stop": {"rect": rect_stop, "message": "Deteniendo la Simulación."}
}

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
        
    elif vehicle_type == "Truck":
        # Rectángulo más largo y alto (camión)
        TRUCK_WIDTH = 40
        TRUCK_HEIGHT = 20
        pygame.draw.rect(surface, color, (x, y, TRUCK_WIDTH, TRUCK_HEIGHT), border_radius=4)
        # Ruedas
        pygame.draw.circle(surface, NEGRO, (x + 8, y + TRUCK_HEIGHT), WHEEL_RADIUS + 1)
        pygame.draw.circle(surface, NEGRO, (x + TRUCK_WIDTH - 8, y + TRUCK_HEIGHT), WHEEL_RADIUS + 1)
        
    elif vehicle_type == "Car":
        # Rectángulo más plano y bajo
        CAR_HEIGHT = 15
        pygame.draw.rect(surface, color, (x, y + 3, VEHICLE_WIDTH - 5, CAR_HEIGHT), border_radius=3)
        # Ruedas
        pygame.draw.circle(surface, NEGRO, (x + 5, y + CAR_HEIGHT + 3), WHEEL_RADIUS)
        pygame.draw.circle(surface, NEGRO, (x + VEHICLE_WIDTH - 10, y + CAR_HEIGHT + 3), WHEEL_RADIUS)

def draw_fleets(surface, base_rect):
    """Dibuja la flota de 10 vehículos en la base, usando menor espaciado."""
    
    # Lista de 10 vehículos
    fleet_composition = [
        ("Jeep", COLOR_JEEP), ("Jeep", COLOR_JEEP), ("Jeep", COLOR_JEEP),
        ("Moto", COLOR_MOTO), ("Moto", COLOR_MOTO),
        ("Truck", COLOR_TRUCK), ("Truck", COLOR_TRUCK),
        ("Car", COLOR_CAR), ("Car", COLOR_CAR), ("Car", COLOR_CAR)
    ]
    
    start_x = base_rect.left + 10
    start_y = base_rect.top + 20
    # Espacio vertical reducido
    spacing = 30 

    for i, (v_type, color) in enumerate(fleet_composition):
        y_pos = start_y + i * spacing
        draw_vehicle(surface, v_type, color, start_x, y_pos)
        
# --- BUCLE PRINCIPAL DEL JUEGO (GAME LOOP) ---
ejecutando = True
while ejecutando:
    # 1. Procesamiento de Eventos
    for evento in pygame.event.get():
        if evento.type == pygame.QUIT:
            ejecutando = False
        
        # Manejo de Clics del Mouse
        if evento.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = evento.pos
            
            # Verificar si se hizo clic en algún botón
            for name, data in botones.items():
                if data["rect"].collidepoint(mouse_pos):
                    print(f"BOTÓN PRESIONADO: {name} | Acción: {data['message']}")
                    # Aquí iría la llamada a la función del GameEngine (e.g., engine.init_game())

    # 2. Lógica del Juego (Vacía por ahora)
    
    # 3. Dibujo
    ventana.fill(BLANCO)

    # A. Dibujar Bases y Terreno de Acción
    # Bases (Fondo rosa claro con borde negro)
    pygame.draw.rect(ventana, ROSA_CLARO, rect_base1, border_radius=10)
    pygame.draw.rect(ventana, NEGRO, rect_base1, 2, border_radius=10)
    pygame.draw.rect(ventana, ROSA_CLARO, rect_base2, border_radius=10)
    pygame.draw.rect(ventana, NEGRO, rect_base2, 2, border_radius=10)

    # Terreno de Acción (Fondo blanco/gris con borde rosa claro)
    pygame.draw.rect(ventana, TERRENO_FONDO, rect_terreno, border_radius=10)
    pygame.draw.rect(ventana, ROSA_CLARO, rect_terreno, 4, border_radius=10)

    # B. Dibujar Títulos
    texto_base1 = fuente_titulo.render("Base 1", True, NEGRO)
    texto_terreno = fuente_titulo.render("Terreno de Accion", True, NEGRO)
    texto_base2 = fuente_titulo.render("Base 2", True, NEGRO)

    ventana.blit(texto_base1, (rect_base1.centerx - texto_base1.get_width() // 2, rect_base1.top - 20))
    ventana.blit(texto_terreno, (rect_terreno.centerx - texto_terreno.get_width() // 2, rect_terreno.top - 20))
    ventana.blit(texto_base2, (rect_base2.centerx - texto_base2.get_width() // 2, rect_base2.top - 20))

    # C. Dibujar la Flota de Vehículos en ambas bases
    draw_fleets(ventana, rect_base1)
    draw_fleets(ventana, rect_base2)
    
    # D. Dibujar Botones de Control y su Texto
    for name, data in botones.items():
        rect = data["rect"]
        color = BLANCO 
        if name == "Init": color = VERDE_INIT
        elif name == "Play": color = AMARILLO_PLAY
        elif name == "Stop": color = GRIS_STOP
        else: color = GRIS_OSCURO_BOTONES
            
        pygame.draw.rect(ventana, color, rect, border_radius=5)
        pygame.draw.rect(ventana, NEGRO, rect, 2, border_radius=5)
        
        texto_boton = fuente_boton.render(name, True, NEGRO)
        ventana.blit(texto_boton, (rect.centerx - texto_boton.get_width() // 2, rect.centery - texto_boton.get_height() // 2))

    # 4. Actualizar la Pantalla
    pygame.display.flip()
    
    # Control de frame rate
    reloj.tick(60)

# --- FINALIZACIÓN ---
pygame.quit()
sys.exit()