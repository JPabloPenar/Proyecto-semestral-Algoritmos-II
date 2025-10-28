from collections import deque

def bfs(grid, start, goal):
    filas, cols = len(grid), len(grid[0])
    cola = deque([start])
    visitados = {start: None}
    
    # Aseguramos que 'camino' esté definida
    camino = [] 

    while cola:
        actual = cola.popleft()
        if actual == goal:
            # Reconstrucción del camino si se encuentra el objetivo
            nodo = goal
            while nodo is not None:
                camino.append(nodo)
                nodo = visitados.get(nodo)
            camino.reverse() 
            break 

        x, y = actual   
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x + dx, y + dy     
            if 0 <= nx < filas and 0 <= ny < cols and grid[nx][ny] == 0:    
                if (nx, ny) not in visitados:
                    cola.append((nx, ny))
                    visitados[(nx, ny)] = actual
    
    # Verificamos si hay camino válido
    if not camino or camino[0] != start:    
        return []
        
    return camino[1:] # Eliminamos la posición inicial


def bfs_multiple_destino(grid, start, targets):
    """
    Realiza una única búsqueda BFS desde 'start' para encontrar los caminos
    más cortos a un conjunto de 'targets' (recursos) en una sola pasada.
    """
    
    filas, cols = len(grid), len(grid[0])
    cola = deque([start])
    visitados = {start: None} # Diccionario para reconstruir el camino {vecino: padre}
    
    # Para almacenar los caminos encontrados
    caminos_encontrados = {} # {destino: camino_reconstruido}
    
    while cola:
        actual = cola.popleft()
        
        # Si el nodo actual es un objetivo (recurso) que no hemos encontrado
        if actual in targets and actual not in caminos_encontrados:
            
            # --- Reconstrucción del Camino ---
            camino = []
            nodo = actual
            while nodo is not None:
                camino.append(nodo)
                nodo = visitados.get(nodo)
            camino.reverse()
            
            # Almacena el camino (excluyendo el punto de inicio)
            caminos_encontrados[actual] = camino[1:]
            
            # Si encontramos todos los objetivos, podemos terminar (optimización extra)
            if len(caminos_encontrados) == len(targets):
                break

        x, y = actual
        
        # Recorre las 4 posiciones posibles (arriba, abajo, izquierda, derecha)
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x + dx, y + dy
            
            # Verifica que la posición esté dentro del mapa y que la celda no sea un obstáculo (0)
            if 0 <= nx < filas and 0 <= ny < cols and grid[nx][ny] == 0:
                if (nx, ny) not in visitados:
                    cola.append((nx, ny))
                    visitados[(nx, ny)] = actual
    
    # --- Selección del Camino Más Corto ---
    mejor_destino = None
    camino_mas_corto = []
    min_longitud = float('inf')
    
    for destino, camino in caminos_encontrados.items():
        if len(camino) < min_longitud:
            min_longitud = len(camino)
            mejor_destino = destino
            camino_mas_corto = camino
            
    # Devuelve el mejor destino y su camino
    return mejor_destino, camino_mas_corto