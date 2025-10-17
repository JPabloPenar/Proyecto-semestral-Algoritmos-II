from collections import deque

def bfs(grid, start, goal):
    #*
    # BFS para encontrar el camino más corto desde 'start' hasta 'goal'
    #grid: matriz 2D (0 = libre, 1 = obstáculo/mina)
    #start, goal: (fila, columna)
    #Devuelve una lista de pasos [(fila, col), ...] para recorrer
    # #
    
    filas, cols = len(grid), len(grid[0])
    cola = deque([start])
    visitados = {start: None}

    while cola:
        actual = cola.popleft()
        if actual == goal:
            break

        x, y = actual   # posición actual en la que hacemos BFS
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:   # recorre las 4 posiciones posibles (arriba, abajo, izquierda, derecha).
            nx, ny = x + dx, y + dy     # calculamos la posición de una nueva celda libre que es candidata a ser el próximo movimiento.
            if 0 <= nx < filas and 0 <= ny < cols and grid[nx][ny] == 0:    # verifica que la posición esté dentro del mapa y que la celda no sea algún obstáculo.
                if (nx, ny) not in visitados:
                    cola.append((nx, ny))   # añadimos la posición vecina para recorrerla en otro momento.
                    visitados[(nx, ny)] = actual    # guardamos la posición para ir armando el camino final hacia el destino.
    
    # Reconstrucción del camino
    camino = [] # lista para guardar el camino desde la posición inical al objetivo.
    nodo = goal
    while nodo is not None: # empezamos desde el objetivo hasta llegar a la posición inicial.
        camino.append(nodo)
        nodo = visitados.get(nodo)
    camino.reverse() # damos vuelta la lista para que vaya desde la posición inicial al final porque append agrega los elementos al final de la lista.

    # Verificamos si hay camino válido
    if not camino or camino[0] != start:    # si la lista está vacía o la primera posición no es el inicio, no hay camino posible.
        return []
    return camino[1:]  # eliminamos la posición inicial porque el vehículo ya está ahí y debe moverse a las otras posiciones.

