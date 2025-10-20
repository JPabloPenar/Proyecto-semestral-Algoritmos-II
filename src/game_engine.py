import os
import sys
import time 
from map_manager import MapManager
from visualization import flota_total
from vehicles import *

class GameEngine:
    def detectar_colisiones(flota):
        posiciones_ocupadas = {}  # { (col, fila): [vehiculo1, vehiculo2, ...] }
        
        # 1. Mapear la posición de cada vehículo
        for veh in flota:
            posicion = (veh.grid_col, veh.grid_fila)
            
            if veh.estado == "explotado": # Omitir vehículos explotados
                continue 

            if posicion not in posiciones_ocupadas:
                posiciones_ocupadas[posicion] = []
            
            posiciones_ocupadas[posicion].append(veh)

        # 2. Comprobar si hay más de un vehículo en cualquier posición
        
        for posicion, vehiculos_en_pos in posiciones_ocupadas.items(): #hay que cambiar esto
            if len(vehiculos_en_pos) > 1:
                vehiculos_en_pos.estado= "explotado"
                

               
    
    