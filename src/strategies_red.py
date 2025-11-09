def moto_chocadora(motos, flota_azul, grid):
    #*
    # Función para que las motos adopten distintas estrategias según el escenario.
    # Persigue a los camiones azules luego de recoger un recurso.
    # *#
    camiones_objetivo = [v for v in flota_azul if v.estado == "activo" and v.__class__.__name__=="camion"]
    
    for moto in motos:
        if moto.estado != "activo":
            continue
        
        # Si ya tiene camino y objetivo, no recalcular
        if moto.camino and moto.objetivo_actual:
            continue
        
        # Seleccionamos el camión azul más cercano
        min_dist = float('inf')
        target_camion = None
        for cam in camiones_objetivo:
            dist = abs(cam.fila - moto.fila) + abs(cam.columna - moto.columna)
            if dist < min_dist:
                min_dist = dist
                target_camion = cam
        
        if target_camion:
            # Actualizamos objetivo y recalculamos camino usando A*
            moto.objetivo_actual = (target_camion.fila, target_camion.columna)
            moto.calcular_camino(grid, moto.objetivo_actual)