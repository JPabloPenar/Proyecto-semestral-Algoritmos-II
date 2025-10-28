# game_engine.py (MODIFICADO)

from map_manager import MapManager 
from resources import Recurso, Persona 
from vehicles import vehicle

# Definición de las zonas de las bases (tomadas de map_manager.py)
# BASE1 (Rojo): min_col=0, max_col=29, min_row=10, max_row=79
# BASE2 (Azul): min_col=130, max_col=159, min_row=10, max_row=79
BASE1_MAX_COL = 29
BASE2_MIN_COL = 130
BASE_MIN_ROW = 10
BASE_MAX_ROW = 79
SAVE_HISTORY_TICK_RATE = 5

def update_simulation(mmanager: MapManager, flota_total: list) -> str:
    """
    Ejecuta un paso de la simulación (un "tick") con lógica de cooldown.

    Args:
        mmanager: La instancia actual de MapManager (el motor del mapa).
        flota_total: La lista de todos los vehículos en la simulación.

    Returns:
        Un mensaje de estado (str) indicando lo que sucedió.
    """
    
    # Avanza la instancia de tiempo. Maneja la aparición/desaparición de Mina G1.
    mmanager.update_time()
    if mmanager.time_instance % SAVE_HISTORY_TICK_RATE == 0:
        mmanager.guardar_estado_historial()

    # Mensajes para registro de eventos
    event_log = []

    for veh in flota_total:
        """
        Lógica de movimiento, actualización de objetivos y colisiones de vehículos.
        """
        
        if veh.estado != "activo":
            continue # Saltar vehículos explotados
        
        # [MODIFICACIÓN 1: Actualizar el cooldown de búsqueda]
        # Se asume que 'search_cooldown' fue agregado a vehicles.py
        if hasattr(veh, 'search_cooldown') and veh.search_cooldown > 0:
            veh.search_cooldown -= 1
        # ---------------------------------------------------
        
        # 1. Movimiento (si hay camino)
        if veh.camino:
            veh.mover_por_camino()

        # 2. Lógica de Objetivos
        
        # A) ¿Está el vehículo en una base?
        is_in_base = False
        if veh.equipo == "Rojo" and BASE1_MAX_COL >= veh.columna >= 0 and BASE_MAX_ROW >= veh.fila >= BASE_MIN_ROW:
            is_in_base = True
        elif veh.equipo == "Azul" and BASE2_MIN_COL <= veh.columna <= MapManager.GRID_COLS_TOTALES - 1 and BASE_MAX_ROW >= veh.fila >= BASE_MIN_ROW:
            is_in_base = True

        # B) Si está en la base Y no tiene viajes pendientes: 
        #    Esto simula la "descarga" y "reabastecimiento" de viajes.
        if is_in_base and veh.viajesActuales < veh.viajesTotales:
            # Lógica de "descarga": Reinicia la capacidad a su máximo
            veh.viajesActuales = veh.viajesTotales 
            veh.objetivo_actual = None # Cancela cualquier objetivo de base
            event_log.append(f"{veh.__class__.__name__} ({veh.equipo}) 'descargó' y está listo para nuevos viajes.")

        # C) Si no tiene objetivo actual O llegó a su objetivo
        veh.actualizar_objetivo(mmanager.grid_maestra)

        # D) Si no tiene objetivo actual: Debe buscar uno (si le quedan viajes) o volver a base.
        if veh.objetivo_actual is None: 
            
            # [MODIFICACIÓN 2: Lógica de Cooldown]
            # Solo busca si el cooldown terminó.
            can_search = not hasattr(veh, 'search_cooldown') or veh.search_cooldown == 0
            
            if can_search:
                
                # --- LÓGICA DE BÚSQUEDA DE RECURSO ---
                if veh.viajesActuales > 0:
                    # Intenta buscar el recurso más cercano. Esta función ya asigna el camino y el objetivo.
                    recurso_encontrado = veh.buscar_recurso_mas_cercano(mmanager.grid_maestra)
                    
                    if recurso_encontrado:
                        event_log.append(f"{veh.__class__.__name__} ({veh.equipo}) inició viaje hacia Recurso en {recurso_encontrado}")
                    else:
                        # Si falló en encontrar recurso O falló en encontrar camino: Aplicar cooldown
                        if hasattr(veh, 'search_cooldown'):
                             veh.search_cooldown = 30 # Esperar 30 ticks antes de volver a intentar
                             event_log.append(f"{veh.__class__.__name__} ({veh.equipo}) Recurso no encontrado o inaccesible. Cooldown.")


                # --- LÓGICA DE VOLVER A BASE ---
                # Si no encontró objetivo (o está en cooldown por fallo anterior) Y no está en base, debe volver a base.
                if veh.objetivo_actual is None and not is_in_base: 
                    # Intenta volver a base.
                    veh.volver_a_base(mmanager.grid_maestra)
                    
                    # Si 'volver_a_base' falló en encontrar camino (veh.camino está vacío)
                    if not veh.camino: 
                        # Aplicar cooldown para no reintentar la costosa búsqueda en cada frame
                        if hasattr(veh, 'search_cooldown'):
                            veh.search_cooldown = 30 
                        event_log.append(f"{veh.__class__.__name__} ({veh.equipo}) Base inaccesible. Cooldown.")
                    else:
                        event_log.append(f"{veh.__class__.__name__} ({veh.equipo}) no encontró recurso y regresa a base.")
            # ----------------------------------------
            # Si está en cooldown, no se ejecuta la búsqueda ni la vuelta a base.


        # 3. Lógica de Colisión (solo si está activo)
        if veh.estado == "activo":
            
            collision_type, entity = mmanager.check_vehicle_collisions(veh)
            
            if collision_type and entity:
                
                if collision_type.startswith("mina"):
                    # El vehículo explota y se desactiva
                    veh.explotar()
                    veh.camino = [] # Detiene el movimiento
                    event_log.append(f"¡Explosión! {veh.__class__.__name__} ({veh.equipo}) en T={mmanager.time_instance}")
                    # TODO: consultar si quitar la mina. Por ahora la dejamos.

                elif collision_type == "recurso":
                    # El vehículo recoge el recurso si su capacidad se lo permite
                    
                    # 1. Verifica compatibilidad
                    compatible = (veh.carga == "todo" or 
                                  (veh.carga == "personas" and isinstance(entity, Persona)) or 
                                  (veh.carga != "personas" and not isinstance(entity, Persona) and veh.carga == "todo")) # redundante con 'todo'

                    if compatible:
                        # 2. Verifica capacidad
                        if veh.viajesActuales > 0:
                            
                            # Recoger: disminuir viajes disponibles y quitar de la grid
                            veh.viajesActuales -= 1 # Disminuye viajesActuales
                            event_log.append(f"({veh.equipo}) recogió Recurso ({entity.__class__.__name__}) en ({veh.columna}, {veh.fila})")
                            
                            # Quitar el recurso de la grid y de la lista de entidades
                            mmanager.grid_maestra[veh.fila][veh.columna] = 0 # Deja la celda libre
                            mmanager.entities.remove(entity)
                            
                            # 3. Al recoger, el vehículo automáticamente debe dirigirse a la base.
                            veh.objetivo_actual = None # Cancela el objetivo (que era el recurso)
                            veh.volver_a_base(mmanager.grid_maestra)
                            
                        else:
                            event_log.append(f"{veh.__class__.__name__} ({veh.equipo}) no puede llevar más carga (Capacidad llena).")
                    else:
                         event_log.append(f"{veh.__class__.__name__} ({veh.equipo}) no es compatible con {entity.__class__.__name__}.")

                
                elif collision_type == "vehiculo":
                    veh.explotar()
                    veh.camino = [] # Detiene el movimiento
                    entity.explotar()
                    entity.camino = []
                    event_log.append(f"Choque de {veh.__class__.__name__} y {entity.__class__.__name__}")
                                                        

    if event_log:
        return " | ".join(event_log)
    else:
        return "Simulación avanzada sin eventos mayores."


def update_and_get_next_state(mmanager: MapManager, flota_total: list) -> tuple[MapManager, str, str]:
    """
    Avanza la simulación un paso (para el botón '>>') y devuelve el nuevo estado.
    
    Nota: La lógica de MapManager.update_time() ya guarda el estado en el historial.
    """

    # 1. Guarda la metadata de historial antes de decrementar (por seguridad en el replay)
    current_history = mmanager.history
    current_base_dir = mmanager.base_dir
    
    # 2. Ejecuta el tick de la simulación y genera eventos
    event_message = update_simulation(mmanager, flota_total)
    
    # El motor 'engine' ya se actualizó en update_simulation y MapManager.update_time()
    
    # 3. La parte de 'carga de nuevo estado' del código original se elimina
    #    porque el 'engine' actual *es* el nuevo estado. Solo actualizamos las
    #    referencias de los vehículos si es necesario (asumimos que la flota 
    #    de 'visualization.py' ya está sincronizada por referencia).
    
    # Retornamos el motor actualizado, el mensaje de estado y el nuevo estado (STOPPED)
    return mmanager, "STOPPED", event_message