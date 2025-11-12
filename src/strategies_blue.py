def moto_chocadora(motos, flota_roja, grid):
    #*
    # Función para que las motos adopten distintas estrategias según el escenario.
    # Persigue a los camiones azules. En el camino, podría colisionar con otro vehículo que no sea camión.
    # *#
    motos_objetivo = [v for v in flota_roja if v.estado == "activo" and v.__class__.__name__=="moto"]
    
    for moto in motos:
        if moto.estado != "activo":
            continue
        
        # Si ya tiene camino y objetivo, no recalcular
        if moto.camino and moto.objetivo_actual:
            continue
        
        # Seleccionamos el camión azul más cercano
        min_dist = float('inf')
        target_moto_roja = None
        for moto_roja in motos_objetivo:
            dist = abs(moto_roja.fila - moto.fila) + abs(moto_roja.columna - moto.columna)
            if dist < min_dist:
                min_dist = dist
                target_moto_roja = moto_roja
        
        if target_moto_roja:
            # Actualizamos objetivo y recalculamos camino usando A*
            moto.objetivo_actual = (target_moto_roja.fila, target_moto_roja.columna)
            moto.calcular_camino(grid, moto.objetivo_actual)