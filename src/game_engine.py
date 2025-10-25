# game_engine.py

from map_manager import MapManager 

def update_simulation(engine: MapManager, flota_total: list) -> str:
    """
    Ejecuta un paso de la simulación (un "tick").

    Args:
        engine: La instancia actual de MapManager (el motor del juego/mapa).
        flota_total: La lista de todos los vehículos en la simulación.

    Returns:
        Un mensaje de estado (str) indicando lo que sucedió.
    """
    
    # Avanza la instancia de tiempo. Maneja la aparición/desaparición de Mina G1.
    engine.update_time()
    
    # Mensajes para registro de eventos
    event_log = []

    for veh in flota_total:
        """
        Lógica de movimiento, actualización de objetivos y colisiones de vehículos.
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
                    event_log.append(f"¡Explosión! {veh.__class__.__name__} ({veh.equipo}) en T={engine.time_instance}")
                    # TODO: consultar si quitar la mina. Por ahora la dejamos.

                elif collision_type == "recurso":
                    # El vehículo recoge el recurso si su capacidad se lo permite
                    if veh.carga == entity.tipoDeCarga or veh.carga == "todo":
                        # Solo recoge si tiene viajes disponibles
                        if veh.viajesActuales > 0:
                            veh.recoger() # Disminuye viajesActuales
                            event_log.append(f"({veh.equipo}) recogió Recurso ({entity.__class__.__name__}) en ({veh.columna}, {veh.fila})")
                            
                            # Quitar el recurso de la grid y de la lista de entidades
                            engine.grid_maestra[veh.fila][veh.columna] = 0 # Deja la celda libre
                            engine.entities.remove(entity)
                        else:
                            event_log.append(f"{veh.__class__.__name__} ({veh.equipo}) no puede llevar más carga (Capacidad llena).")
                
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


def update_and_get_next_state(engine: MapManager, flota_total: list) -> tuple[MapManager, str, str]:
    """
    Avanza la simulación un paso (para el botón '>>') y devuelve el nuevo estado.
    
    Nota: La lógica de MapManager.update_time() ya guarda el estado en el historial.
    """

    # 1. Guarda la metadata de historial antes de decrementar (por seguridad en el replay)
    current_history = engine.history
    current_base_dir = engine.base_dir
    
    # 2. Ejecuta el tick de la simulación y genera eventos
    event_message = update_simulation(engine, flota_total)
    
    # El motor 'engine' ya se actualizó en update_simulation y MapManager.update_time()
    
    # 3. La parte de 'carga de nuevo estado' del código original se elimina
    #    porque el 'engine' actual *es* el nuevo estado. Solo actualizamos las
    #    referencias de los vehículos si es necesario (asumimos que la flota 
    #    de 'visualization.py' ya está sincronizada por referencia).
    
    # Retornamos el motor actualizado, el mensaje de estado y el nuevo estado (STOPPED)
    return engine, "STOPPED", event_message