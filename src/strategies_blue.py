from vehicles import moto, camion
from resources import Recurso

def moto_defensora(flota_roja, flota_azul, grid):
    motos_azules = [v for v in flota_azul if isinstance(v, moto) and v.estado == "activo"]
    motos_rojas = [v for v in flota_roja if isinstance(v, moto) and v.estado == "activo"]
    
    for moto_azul in motos_azules:
        moto_azul.liberar_recurso(grid)
        if moto_azul.estado != "activo":
            continue
        min_dist = float('inf')
        target_moto_roja = None
        for mr in motos_rojas:
            dist = abs(mr.fila - moto_azul.fila) + abs(mr.columna - moto_azul.columna)
            if dist < min_dist:
                min_dist = dist
                target_moto_roja = mr

        if target_moto_roja:
            # 3. Asignar el objetivo y calcular el camino con A*
            moto_azul.objetivo_actual = (target_moto_roja.fila, target_moto_roja.columna)
            moto_azul.calcular_camino(grid, moto_azul.objetivo_actual)
            continue  # Ya tiene objetivo, pasamos al siguiente vehículo

def escape_camion(flota_roja, flota_azul, grid, mmanager):
    
    BASE_MIN_ROW = 10
    BASE_MAX_ROW = 79
    BASE2_MIN_COL = 130  # Base azul
    camiones_equipo = [v for v in flota_azul if isinstance(v, camion)]

    for cam in camiones_equipo:
        # --- Detectar si hay un enemigo cercano ---
        enemigo_cercano = any(
            abs(otro.fila - cam.fila) + abs(otro.columna - cam.columna) <= 5
            for otro in flota_roja
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
        if (BASE2_MIN_COL <= cam.columna <= mmanager.GRID_COLS_TOTALES - 1
            and BASE_MAX_ROW >= cam.fila >= BASE_MIN_ROW):
            
            # Sólo si no tiene objetivo actual, lo mandamos a buscar
            if cam.objetivo_actual is None and not enemigo_cercano:
                cam.buscar_recurso_mas_cercano(grid)
