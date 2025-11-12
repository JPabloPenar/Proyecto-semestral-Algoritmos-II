from vehicles import camion, moto, auto, jeep
from resources import Recurso

#*
# ESTRATEGIA EQUIPO ROJO
# 1. Atacar con las dos motos a los camiones intentando que exploten.
# 2. Si los camiones detectan vehículos enemigos a un radio de 5 celdas,
# volverán a base siempre y cuando tengan recursos agarrados.
# 3. Un auto rojo a la vez perseguirá a un jeep azul enemigo siempre y cuando 
# el auto rojo no tenga recursos y el jeep azul no esté en base.
# *#

def moto_chocadora(flota_roja, flota_azul, grid):
    camiones_azules = [v for v in flota_azul if isinstance(v, camion) and v.estado == "activo"]
    motos_rojas = [v for v in flota_roja if isinstance(v, moto) and v.estado == "activo"]
    
    for moto_roja in motos_rojas:
        moto_roja.liberar_recurso(grid)
        if moto_roja.estado != "activo":
            continue

        if camiones_azules:
            # Elegimos el camión más cercano usando Manhattan
            min_dist = float('inf')
            target_camion = None
            for c in camiones_azules:
                dist = abs(c.fila - moto_roja.fila) + abs(c.columna - moto_roja.columna)
                if dist < min_dist:
                    min_dist = dist
                    target_camion = c

            if target_camion:
                moto_roja.objetivo_actual = (target_camion.fila, target_camion.columna)
                moto_roja.calcular_camino(grid, moto_roja.objetivo_actual)
                continue  # Ya tiene objetivo, pasamos al siguiente vehículo

def camion_asustadizo(flota_roja, flota_azul, grid, mmanager):
    
    BASE_ROW_MIN = 10
    BASE_ROW_MAX = 79
    BASE_COL_MAX = 29  # Límite derecho de la base roja
    camiones_equipo = [v for v in flota_roja if isinstance(v, camion)]

    for cam in camiones_equipo:
        # --- Detectar si hay un enemigo cercano ---
        enemigo_cercano = any(
            abs(otro.fila - cam.fila) + abs(otro.columna - cam.columna) <= 5
            for otro in flota_azul
            if otro.estado == "activo"
        )

        # --- Si hay enemigo cerca, el camión huye a la base ---
        if enemigo_cercano and cam.recursos != []:
            cam.volver_a_base(grid)
            cam.liberar_recurso(grid)
            continue
        
        hay_recursos = any(isinstance(e, Recurso) for e in mmanager.entities)

        if not hay_recursos:
            # Solo hacer algo si el camión tiene recursos pendientes
            if cam.recursos:
                cam.volver_a_base(grid)
                cam.liberar_recurso(grid)
            # Si no lleva nada, no hace nada → se salta
            continue
        
        # --- Si no hay enemigo y el camión está dentro del área de la base ---
        if (0 <= cam.columna <= BASE_COL_MAX) and (BASE_ROW_MIN <= cam.fila <= BASE_ROW_MAX):
            # Sólo si no tiene objetivo actual, lo mandamos a buscar
            if cam.objetivo_actual is None and not enemigo_cercano:
                cam.buscar_recurso_mas_cercano(grid)

def auto_asesino(flota_roja, flota_azul, grid, mmanager):
    # Un solo auto rojo a la vez persigue al jeep azul más cercano siempre que el auto no tenga recursos y el jeep azul no esté en base.
    base_azul = {"min_col": 130, "max_col": 159, "min_row": 10, "max_row": 79}

    # Filtrar autos rojos activos
    autos_rojos = [v for v in flota_roja if isinstance(v, auto) and v.estado == "activo"]
    if not autos_rojos:
        return

    # Filtrar jeeps azules activos
    jeeps_azules = [v for v in flota_azul if isinstance(v, jeep) and v.estado == "activo" and not mmanager._en_base(v, base_azul)]
    if not jeeps_azules:
        return
    
    # Elegimos un solo auto para atacar
    
    atacante = autos_rojos[0]
    
    atacante.liberar_recurso(grid)
    
    # Buscar el jeep más cercano
    fila_att, col_att = atacante.fila, atacante.columna
    objetivo = min(jeeps_azules, key=lambda j: abs(j.fila - fila_att) + abs(j.columna - col_att))

    # Asignar objetivo y calcular camino
    if atacante.recursos == []:
        atacante.objetivo_actual = (objetivo.fila, objetivo.columna)
        atacante.calcular_camino(grid, atacante.objetivo_actual)
    
    if not jeeps_azules:
        return