from map_manager import MapManager 
from resources import Persona, Recurso 
from vehicles import moto, camion

BASE1_MAX_COL = 29
BASE2_MIN_COL = 130
BASE_MIN_ROW = 10
BASE_MAX_ROW = 79

def update_simulation(mmanager: MapManager, flota_total: list) -> str:
    
    mmanager.update_time()

    camiones_azules = [
                    v for v in mmanager.vehicles 
                    if v.equipo == "Azul" and isinstance(v, camion) and v.estado == "activo"
                ]
    

    motos_rojas = [
        v for v in mmanager.vehicles 
        if v.equipo == "Rojo" and isinstance(v, moto) and v.estado == "activo"
    ]
    
    for veh in flota_total:
        
        if veh.estado != "activo" and veh.estado != "en_cooldown":
            if mmanager.grid_maestra[veh.fila][veh.columna] == veh:
                mmanager._marcar_vehiculo(veh, valor=0) 
            continue

        # 1. Actualizar el cooldown de búsqueda
        if hasattr(veh, 'search_cooldown'):
            if veh.search_cooldown > 0:
                veh.search_cooldown -= 1
                veh.estado = "en_cooldown"
                veh.liberar_recurso(mmanager.grid_maestra)
            elif veh.estado == "en_cooldown" and veh.search_cooldown == 0:
                veh.estado = "activo"

        # 2. Movimiento (si hay camino)
        # ... (código que maneja el movimiento, colisión con minas, y marcaje)
        if veh.camino:
            # Se limpia la celda ANTERIOR antes de mover
            mmanager._marcar_vehiculo(veh, valor=0) 
            veh.mover_por_camino()
            
            # --- CORRECCIÓN DE COLISIÓN DE MINAS (Chequeo ANTES de marcar) ---
            collision_type, entity = mmanager.check_vehicle_collisions(veh)
            
            if collision_type and collision_type.startswith("mina"):
                
                veh.liberar_recurso(mmanager.grid_maestra)
                mmanager._marcar_vehiculo(veh, valor=0) 
                veh.explotar() # Cambia estado a 'inactivo'
                veh.camino = []
                continue # Pasa al siguiente vehículo

            # Se marca la celda NUEVA después de mover (Solo si no explotó con mina)
            mmanager._marcar_vehiculo(veh) 
        

        # 3. Lógica de Objetivos

        # A) ¿Está el vehículo en una base?
        is_in_base = False
        if veh.equipo == "Rojo" and BASE1_MAX_COL >= veh.columna >= 0 and BASE_MAX_ROW >= veh.fila >= BASE_MIN_ROW:
            is_in_base = True
        elif veh.equipo == "Azul" and BASE2_MIN_COL <= veh.columna <= MapManager.GRID_COLS_TOTALES - 1 and BASE_MAX_ROW >= veh.fila >= BASE_MIN_ROW:
            is_in_base = True

        if is_in_base and veh.recursos:
            mmanager._entregar_recursos(veh)

        # B) Si está en la base Y no tiene viajes pendientes: 
        if is_in_base and veh.viajesActuales < veh.viajesTotales:
            veh.viajesActuales = veh.viajesTotales 
            veh.objetivo_actual = None
            if veh.viajesActuales > 0 and veh.objetivo_actual is None:
                veh.buscar_recurso_mas_cercano(mmanager.grid_maestra)
                continue
        
        if veh.objetivo_actual is not None and veh.camino:
            target_fila, target_col = veh.objetivo_actual

            if mmanager.grid_maestra[target_fila][target_col] == 0:

                veh.objetivo_actual = None
                veh.camino = []

        # C) Si no tiene objetivo actual O llegó a su objetivo
        # SÓLO ocurra si el vehículo está realmente en la celda final Y camino está vacío.
        veh.actualizar_objetivo(mmanager.grid_maestra)

        # D) Si no tiene objetivo actual: Debe buscar uno (si le quedan viajes) o volver a base.
        if isinstance(veh, moto) and veh.equipo == "Rojo" and camiones_azules:
                    # Elegimos el camión más cercano usando Manhattan
            min_dist = float('inf')
            target_camion = None
            for c in camiones_azules:
                dist = abs(c.fila - veh.fila) + abs(c.columna - veh.columna)
                if dist < min_dist:
                    min_dist = dist
                    target_camion = c

            if target_camion:
                veh.objetivo_actual = (target_camion.fila, target_camion.columna)
                veh.calcular_camino(mmanager.grid_maestra, veh.objetivo_actual)
                continue  # Ya tiene objetivo, pasamos al siguiente vehículo

        elif isinstance(veh, moto) and veh.equipo == "Azul" and motos_rojas:
            min_dist = float('inf')
            target_moto_roja = None
            for mr in motos_rojas:
                dist = abs(mr.fila - veh.fila) + abs(mr.columna - veh.columna)
                if dist < min_dist:
                    min_dist = dist
                    target_moto_roja = mr

            if target_moto_roja:
                # 3. Asignar el objetivo y calcular el camino con A*
                veh.objetivo_actual = (target_moto_roja.fila, target_moto_roja.columna)
                veh.calcular_camino(mmanager.grid_maestra, veh.objetivo_actual)
                continue  # Ya tiene objetivo, pasamos al siguiente vehículo
        
        
        if veh.objetivo_actual is None: 
            
            # Para motos rojas: prioridad atacar camiones azules
            if isinstance(veh, moto) and veh.equipo == "Rojo":

                if camiones_azules:
                    # Elegimos el camión más cercano usando Manhattan
                    min_dist = float('inf')
                    target_camion = None
                    for c in camiones_azules:
                        dist = abs(c.fila - veh.fila) + abs(c.columna - veh.columna)
                        if dist < min_dist:
                            min_dist = dist
                            target_camion = c

                    if target_camion:
                        veh.objetivo_actual = (target_camion.fila, target_camion.columna)
                        veh.calcular_camino(mmanager.grid_maestra, veh.objetivo_actual)
                        continue  # Ya tiene objetivo, pasamos al siguiente vehículo
            
            if isinstance(veh, moto) and veh.equipo == "Azul" and motos_rojas:
                min_dist = float('inf')
                target_moto_roja = None
                for mr in motos_rojas:
                    dist = abs(mr.fila - veh.fila) + abs(mr.columna - veh.columna)
                    if dist < min_dist:
                        min_dist = dist
                        target_moto_roja = mr

                if target_moto_roja:
                    # 3. Asignar el objetivo y calcular el camino con A*
                    veh.objetivo_actual = (target_moto_roja.fila, target_moto_roja.columna)
                    veh.calcular_camino(mmanager.grid_maestra, veh.objetivo_actual)
                    continue  # Ya tiene objetivo, pasamos al siguiente vehículo

            # Solo busca si el cooldown terminó Y no está volviendo a base.
            current_cooldown = veh.search_cooldown if hasattr(veh, 'search_cooldown') else 0
            can_search = current_cooldown == 0
            
            if can_search:

                if veh.viajesActuales > 0:
                    recurso_encontrado = veh.buscar_recurso_mas_cercano(mmanager.grid_maestra)
                    
                    if not recurso_encontrado: 
                        # Si FALLA la búsqueda (no hay recursos accesibles)
                        
                        # Si no encontró objetivo Y no está en base: intenta volver a base.
                        if veh.objetivo_actual is None and not is_in_base: 
                            veh.volver_a_base(mmanager.grid_maestra)
                            
                        # Si 'volver_a_base' falló en encontrar camino, establece el cooldown
                        if not veh.camino and hasattr(veh, 'search_cooldown'): 
                            veh.search_cooldown = 1
                            # No establecemos el estado aquí, se establecerá 'en_cooldown' en el siguiente tick.


                # --- LÓGICA DE VOLVER A BASE (Si agotó viajes o la búsqueda anterior no lo movió) ---
                if veh.objetivo_actual is None and not is_in_base: 
                    veh.volver_a_base(mmanager.grid_maestra)
                    
                    # Si 'volver_a_base' falló en encontrar camino
                    if not veh.camino and hasattr(veh, 'search_cooldown'): 
                        veh.search_cooldown = 1
            # Si está en cooldown, el 'continue' inicial lo salta.
            
            
            # Para motos rojas: prioridad atacar camiones azules
            if isinstance(veh, moto) and veh.equipo == "Rojo":

                if camiones_azules:
                    # Elegimos el camión más cercano usando Manhattan
                    min_dist = float('inf')
                    target_camion = None
                    for c in camiones_azules:
                        dist = abs(c.fila - veh.fila) + abs(c.columna - veh.columna)
                        if dist < min_dist:
                            min_dist = dist
                            target_camion = c

                    if target_camion:
                        veh.objetivo_actual = (target_camion.fila, target_camion.columna)
                        veh.calcular_camino(mmanager.grid_maestra, veh.objetivo_actual)
                        continue  # Ya tiene objetivo, pasamos al siguiente vehículo

            
            # La bandera cooldown_just_set ya no se necesita aquí porque el estado 'en_cooldown'
            # y el 'continue' al inicio del bucle manejan la espera.


        # 4. Lógica de Colisión (solo si está activo)
        if veh.estado == "activo":
            
            # ... (Lógica de colisiones con recursos y vehículos)
            collision_type, entity = mmanager.check_vehicle_collisions(veh)
            
            if collision_type and entity:
                
                if collision_type == "recurso":
                    
                    compatible = (veh.carga == "todo" or 
                                  (veh.carga == "personas" and isinstance(entity, Persona)))

                    if compatible and veh.viajesActuales > 0:
                        
                        # Al recoger el recurso, debemos liberar la reserva (aunque el recurso se vaya a eliminar)
                        if veh.equipo in entity.buscado:
                            entity.buscado.remove(veh.equipo) 
                            
                        veh.viajesActuales -= 1
                        mmanager.grid_maestra[veh.fila][veh.columna] = 0
                        if entity in mmanager.entities:
                            mmanager.entities.remove(entity)    
                        veh.recursos.append(entity)
                        veh.liberar_recurso(mmanager.grid_maestra)
                        veh.objetivo_actual = None
                        if veh.viajesActuales == 0:
                            veh.volver_a_base(mmanager.grid_maestra)

                
                elif collision_type == "vehiculo":
                    if veh.equipo == entity.equipo:
                        return
                    veh.liberar_recurso(mmanager.grid_maestra)
                    
                    mmanager._marcar_vehiculo(veh, valor=0)
                    veh.explotar() # Cambia estado a 'inactivo'
                    veh.camino = []
                    veh.liberar_recurso(mmanager.grid_maestra)
                    mmanager._marcar_vehiculo(entity, valor=0)
                    entity.explotar() # Cambia estado a 'inactivo'
                    entity.camino = []

    if mmanager.check_condiciones_parada():
        
        # Esto solo se ejecuta si check_condiciones_parada() devuelve True
        
        # Calcular el resultado final (mensaje)
        if mmanager.puntajes['Rojo'] > mmanager.puntajes['Azul']:
            resultado_final = "Ganador: Equipo Rojo"
        elif mmanager.puntajes['Azul'] > mmanager.puntajes['Rojo']:
            resultado_final = "Ganador: Equipo Azul"
        else:
            resultado_final = "Empate"

        # **PASO CLAVE: Guardar el resultado en el historial de partidas**
        mmanager._guardar_resultado_partida(resultado_final)

        mmanager._saved_sim_state = "TERMINADO"
        mmanager._guardar_ejecucion_completa(mmanager._saved_sim_state)

        # Retornar el resultado para ser usado por la función de visualización/control
        return "SIMULATION_ENDED"

    return ""


def update_and_get_next_state(mmanager: MapManager, flota_total: list) -> tuple[MapManager, str, str]:
    
    event_message = update_simulation(mmanager, flota_total)
    
    return mmanager, "STOPPED", event_message