from map_manager import MapManager 
from resources import Persona, Recurso 

BASE1_MAX_COL = 29
BASE2_MIN_COL = 130
BASE_MIN_ROW = 10
BASE_MAX_ROW = 79

def update_simulation(mmanager: MapManager, flota_total: list) -> str:
    
    mmanager.update_time()

    for veh in flota_total:
        
        if veh.estado != "activo":
            if mmanager.grid_maestra[veh.fila][veh.columna] == veh:
                mmanager._marcar_vehiculo(veh, valor=0) 
            continue

        # 1. Actualizar el cooldown de búsqueda
        if hasattr(veh, 'search_cooldown') and veh.search_cooldown > 0:
            veh.search_cooldown -= 1
        
        # 2. Movimiento (si hay camino)
        if veh.camino:

            # Se limpia la celda ANTERIOR antes de mover
            mmanager._marcar_vehiculo(veh, valor=0) 
            veh.mover_por_camino()
            
            # --- CORRECCIÓN DE COLISIÓN DE MINAS (Chequeo ANTES de marcar) ---
            collision_type, entity = mmanager.check_vehicle_collisions(veh)
            
            if collision_type and collision_type.startswith("mina"):
                
                # LÓGICA DE LIBERACIÓN DE RECURSO (si el vehículo explotado tenía una reserva):
                if veh.objetivo_actual:
                    target_fila, target_col = veh.objetivo_actual
                    recurso_objetivo = mmanager.grid_maestra[target_fila][target_col]
                    
                    # Solo libera si es un Recurso Y está reservado por ESTE equipo
                    if isinstance(recurso_objetivo, Recurso) and recurso_objetivo.buscado == veh.equipo:
                        recurso_objetivo.buscado = None # Liberar la reserva
                # FIN LÓGICA DE LIBERACIÓN
                
                # Si choca con una mina, explota ANTES de marcarse en la nueva posición.
                # Esto garantiza que el vehículo nunca sobrescriba el '1' de la mina.
                mmanager._marcar_vehiculo(veh, valor=0) 
                veh.explotar()
                veh.camino = []
                continue # Pasa al siguiente vehículo
            # -----------------------------------------------------------------

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

        # C) Si no tiene objetivo actual O llegó a su objetivo
        # NOTA: La lógica en vehicle.py ahora se asegura de que objetivo_actual=None 
        # SÓLO ocurra si el vehículo está realmente en la celda final Y camino está vacío.
        veh.actualizar_objetivo(mmanager.grid_maestra)

        # D) Si no tiene objetivo actual: Debe buscar uno (si le quedan viajes) o volver a base.
        if veh.objetivo_actual is None: 
            
            # Solo busca si el cooldown terminó Y no está volviendo a base.
            current_cooldown = veh.search_cooldown if hasattr(veh, 'search_cooldown') else 0
            can_search = current_cooldown == 0
            
            cooldown_just_set = False # Bandera para evitar que vuelva a base inmediatamente si la búsqueda falla.

            if can_search:
                
                # --- LÓGICA DE BÚSQUEDA DE RECURSO ---
                if veh.viajesActuales > 0:
                    recurso_encontrado = veh.buscar_recurso_mas_cercano(mmanager.grid_maestra)
                    
                    if not recurso_encontrado: # Si FALLA la búsqueda (no hay recursos o el camino está bloqueado)
                        # Establecer el cooldown y activar la bandera
                        veh.search_cooldown = 30 
                        cooldown_just_set = True


                # --- LÓGICA DE VOLVER A BASE (CORREGIDA) ---
                # Si no encontró objetivo Y no está en base, debe volver a base.
                # Se añade 'and not cooldown_just_set' para que el vehículo se quede esperando el cooldown si la búsqueda falló.
                if veh.objetivo_actual is None and not is_in_base and not cooldown_just_set: 
                    veh.volver_a_base(mmanager.grid_maestra)
                    
                    # Si 'volver_a_base' falló en encontrar camino
                    if not veh.camino and hasattr(veh, 'search_cooldown'): 
                        veh.search_cooldown = 30 
            # Si está en cooldown, no se ejecuta la búsqueda ni la vuelta a base.


        # 4. Lógica de Colisión (solo si está activo)
        if veh.estado == "activo":
            
            # Las colisiones de MINA ya se manejaron en el paso 2.
            # Aquí manejamos colisiones con RECURSOS y VEHÍCULOS.
            collision_type, entity = mmanager.check_vehicle_collisions(veh)
            
            if collision_type and entity:
                
                # if collision_type.startswith("mina"): <-- ESTE CASO SE ELIMINA/IGNORA
                
                if collision_type == "recurso":
                    
                    compatible = (veh.carga == "todo" or 
                                  (veh.carga == "personas" and isinstance(entity, Persona)))

                    if compatible and veh.viajesActuales > 0:
                        veh.recursos.append(entity)
                        
                        # Al recoger el recurso, debemos liberar la reserva (aunque el recurso se vaya a eliminar)
                        if entity.buscado == veh.equipo:
                            entity.buscado = None 
                            
                        veh.viajesActuales -= 1
                        mmanager.grid_maestra[veh.fila][veh.columna] = 0
                        if entity in mmanager.entities:
                            mmanager.entities.remove(entity)    
                        
                        veh.objetivo_actual = None
                        if veh.viajesActuales == veh.viajesTotales:
                            
                            veh.volver_a_base(mmanager.grid_maestra)

                
                elif collision_type == "vehiculo":
                    if veh.equipo == entity.equipo:
                        return
                    # LÓGICA DE LIBERACIÓN PARA VEHÍCULO 1 (veh)
                    if veh.objetivo_actual:
                        target_fila, target_col = veh.objetivo_actual
                        recurso_objetivo = mmanager.grid_maestra[target_fila][target_col]
                        if isinstance(recurso_objetivo, Recurso) and recurso_objetivo.buscado == veh.equipo:
                            recurso_objetivo.buscado = None 
                    
                    mmanager._marcar_vehiculo(veh, valor=0)
                    veh.explotar()
                    veh.camino = []
                    
                    # LÓGICA DE LIBERACIÓN PARA VEHÍCULO 2 (entity)
                    if entity.objetivo_actual:
                        target_fila, target_col = entity.objetivo_actual
                        recurso_objetivo = mmanager.grid_maestra[target_fila][target_col]
                        if isinstance(recurso_objetivo, Recurso) and recurso_objetivo.buscado == entity.equipo:
                            recurso_objetivo.buscado = None 

                    mmanager._marcar_vehiculo(entity, valor=0)
                    entity.explotar()
                    entity.camino = []
                                                        

    return


def update_and_get_next_state(mmanager: MapManager, flota_total: list) -> tuple[MapManager, str, str]:
    
    event_message = update_simulation(mmanager, flota_total)
    
    return mmanager, "STOPPED", event_message