# game_engine.py (OPTIMIZADO CON COOLDOWN)

from map_manager import MapManager 
from resources import Recurso, Persona 
from vehicles import vehicle

BASE1_MAX_COL = 29
BASE2_MIN_COL = 130
BASE_MIN_ROW = 10
BASE_MAX_ROW = 79

def update_simulation(mmanager: MapManager, flota_total: list) -> str:
    
    mmanager.update_time()
    mmanager.guardar_estado_historial()


    for veh in flota_total:
        
        if veh.estado != "activo":
            # Asegurarse de que el vehículo "inactivo" esté borrado de la grid
            # Asumiendo que flota_total incluye todos los vehículos, activos o no.
            # Esto solo se ejecutaría una vez al explotar.
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
            # Se marca la celda NUEVA después de mover
            mmanager._marcar_vehiculo(veh) 

        # 3. Lógica de Objetivos

        # A) ¿Está el vehículo en una base?
        is_in_base = False
        if veh.equipo == "Rojo" and BASE1_MAX_COL >= veh.columna >= 0 and BASE_MAX_ROW >= veh.fila >= BASE_MIN_ROW:
            is_in_base = True
        elif veh.equipo == "Azul" and BASE2_MIN_COL <= veh.columna <= MapManager.GRID_COLS_TOTALES - 1 and BASE_MAX_ROW >= veh.fila >= BASE_MIN_ROW:
            is_in_base = True

        # B) Si está en la base Y no tiene viajes pendientes: 
        if is_in_base and veh.viajesActuales < veh.viajesTotales:
            veh.viajesActuales = veh.viajesTotales 
            veh.objetivo_actual = None

        # C) Si no tiene objetivo actual O llegó a su objetivo
        veh.actualizar_objetivo(mmanager.grid_maestra)

        # D) Si no tiene objetivo actual: Debe buscar uno (si le quedan viajes) o volver a base.
        if veh.objetivo_actual is None: 
            
            # Chequea si el vehículo está en camino a su base (para evitar buscar recursos mientras regresa)
            # Solo busca si el cooldown terminó Y no está volviendo a base.
            can_search = not hasattr(veh, 'search_cooldown') or veh.search_cooldown == 0
            
            if can_search:
                
                # --- LÓGICA DE BÚSQUEDA DE RECURSO ---
                if veh.viajesActuales > 0:
                    recurso_encontrado = veh.buscar_recurso_mas_cercano(mmanager.grid_maestra)
                    
                    if not recurso_encontrado and hasattr(veh, 'search_cooldown'):
                        # Si FALLA la búsqueda (no hay recursos o el camino está bloqueado)
                        veh.search_cooldown = 30 # Esperar 30 ticks antes de volver a intentar


                # --- LÓGICA DE VOLVER A BASE ---
                # Si no encontró objetivo (o está en cooldown por fallo anterior) Y no está en base, debe volver a base.
                if veh.objetivo_actual is None and not is_in_base: 
                    veh.volver_a_base(mmanager.grid_maestra)
                    
                    # Si 'volver_a_base' falló en encontrar camino
                    if not veh.camino and hasattr(veh, 'search_cooldown'): 
                        veh.search_cooldown = 30 
            # Si está en cooldown, no se ejecuta la búsqueda ni la vuelta a base.


        # 4. Lógica de Colisión (solo si está activo)
        if veh.estado == "activo":
            
            collision_type, entity = mmanager.check_vehicle_collisions(veh)
            
            if collision_type and entity:
                
                if collision_type.startswith("mina"):
                    mmanager._marcar_vehiculo(veh, valor=0) 
                    veh.explotar()
                    veh.camino = []

                elif collision_type == "recurso":
                    
                    compatible = (veh.carga == "todo" or 
                                  (veh.carga == "personas" and isinstance(entity, Persona)))

                    if compatible and veh.viajesActuales > 0:
                        veh.viajesActuales -= 1
                        mmanager.grid_maestra[veh.fila][veh.columna] = 0
                        if entity in mmanager.entities:
                            mmanager.entities.remove(entity)    
                        
                        veh.objetivo_actual = None
                        veh.volver_a_base(mmanager.grid_maestra)

                
                elif collision_type == "vehiculo":
                    mmanager._marcar_vehiculo(veh, valor=0)
                    veh.explotar()
                    veh.camino = []
                    mmanager._marcar_vehiculo(entity, valor=0)
                    entity.explotar()
                    entity.camino = []
                                                        

    return


def update_and_get_next_state(mmanager: MapManager, flota_total: list) -> tuple[MapManager, str, str]:
    
    current_history = mmanager.history
    current_base_dir = mmanager.base_dir
    
    event_message = update_simulation(mmanager, flota_total)
    
    return mmanager, "STOPPED", event_message