from src.map_manager import *
from src.visualization import *
import os

def initialize_simulation(load_partida_filename: str = None) -> MapManager:
    """
    Crea e inicializa el MapManager. 
    Intenta cargar una partida guardada si se especifica, 
    o distribuye nuevas entidades si no se especifica o falla la carga.
    """

    mmanager = MapManager()

    if load_partida_filename and os.path.exists(load_partida_filename):
        # 1. Intentar cargar la partida (si el archivo existe)
        try:
            mmanager = mmanager.cargar_partida_inicial(load_partida_filename)
            print(f"Partida cargada exitosamente desde: {load_partida_filename}")
        except Exception as e:
            print(f"Advertencia: Falló la carga de la partida ({e}). Inicializando una nueva...")
            # Si falla la carga, volvemos a distribuir.
            mmanager.distribute_entities()
    else:
        # 2. Inicializar con entidades nuevas (partida nueva)
        mmanager.distribute_entities()

#Guardar el estado inicial en el historial para el replay (Estado 0)
    mmanager.guardar_estado_historial()

    return mmanager

if __name__ == '__main__':
    manager = initialize_simulation()
    main_loop()