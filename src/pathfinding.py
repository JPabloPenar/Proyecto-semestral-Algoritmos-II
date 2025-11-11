from collections import deque
import heapq # Necesario para la cola de prioridad de A*

def manhattan_distance(p1, p2):
    """Heurística: Distancia de Manhattan (cuadrícula)."""
    # p1 y p2 son tuplas (fila, columna)
    return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])


def a_star(grid, start, goal):
    """
    Busca el camino más corto de 'start' a 'goal' usando el algoritmo A*.
    Permite acceder al nodo 'goal' aunque sea un obstáculo.
    """
    filas, cols = len(grid), len(grid[0])
    
    # g_score: Almacena el costo real (G) para llegar a cada nodo desde el inicio.
    # Se inicializa el nodo de inicio con costo 0.
    g_score = {start: 0} 

    # f_score: Almacena el costo total estimado (F = G + H) de cada nodo.
    # Se inicializa el nodo de inicio usando G=0 + la heurística (Manhattan).
    f_score = {start: manhattan_distance(start, goal)}

    # cola_prioridad: Una min-heap que almacena los nodos por explorar.
    # La estructura de heap asegura que siempre se extraiga el nodo con el F-score más bajo.
    cola_prioridad = [(f_score[start], start)]

    # visitados (came_from): Almacena la relación {vecino: padre} para reconstruir el camino.
    # Se inicializa el nodo de inicio sin padre.
    visitados = {start: None}

    # El bucle se ejecuta mientras haya nodos por explorar en la cola.
    while cola_prioridad:
        # Extraer el nodo con el f_score más bajo
        _, actual = heapq.heappop(cola_prioridad)

        if actual == goal:
            # Reconstrucción: Se sigue el rastro de 'visitados' (padres) desde el objetivo
            # hasta el inicio para obtener el camino más corto.
            # El camino se retorna sin incluir el punto de inicio.

            camino = []
            nodo = goal
            while nodo is not None:
                camino.append(nodo)
                # Usamos visitados para rastrear el padre
                nodo = visitados.get(nodo) 
            camino.reverse()
            # Retorna el camino excluyendo la posición inicial
            return camino[1:]

        x, y = actual   
        # Explorar vecinos
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x + dx, y + dy     
            neighbor = (nx, ny)

            # Comprobación de límites (DEBE ir primero)
            if 0 <= nx < filas and 0 <= ny < cols:
                
                # Comprobación de accesibilidad: libre (0) O el destino final
                can_step = grid[nx][ny] == 0 or neighbor == goal
                
                if can_step:
                    # 1. Calcular el G-score tentativo (costo real para llegar al vecino a través del nodo 'actual').
                    tentative_g_score = g_score[actual] + 1
                    
                    # 2. Verificación de mejora: Compara el costo tentativo con el mejor G-score conocido del vecino.
                    if tentative_g_score < g_score.get(neighbor, float('inf')):
                        
                        # 3. Actualizar la Ruta: Se ha encontrado un camino más corto.
                        visitados[neighbor] = actual    # Asigna el nodo 'actual' como el nuevo padre.
                        g_score[neighbor] = tentative_g_score   # Almacena el nuevo G-score más bajo.
                        
                        # 4. Calcular F-score: Calcula el costo total estimado (G + H) del vecino.
                        new_f_score = tentative_g_score + manhattan_distance(neighbor, goal)
                        f_score[neighbor] = new_f_score
                        
                        # 5. Añadir/Actualizar Cola: El vecino se añade (o se actualiza su prioridad) en la cola 
                        # para ser explorado en el futuro, priorizando el costo más bajo.
                        heapq.heappush(cola_prioridad, (new_f_score, neighbor))
                        
    return [] # No se encontró camino

# Mantenemos bfs_multiple_destino porque la lógica de A* múltiple es más compleja
# y el cooldown mitigará su costo.
def bfs_multiple_destino(grid, start, targets, vT):
    """
    Realiza una única búsqueda BFS desde 'start' para encontrar los caminos
    más cortos a un conjunto de 'targets' (recursos) en una sola pasada.
    """
    
    filas, cols = len(grid), len(grid[0])
    cola = deque([start])
    visitados = {start: None} # Diccionario para reconstruir el camino {vecino: padre}
    caminos_encontrados = {} # {destino: camino_reconstruido}
    
    while cola:
        actual = cola.popleft()
        
        if actual in targets and actual not in caminos_encontrados:
            camino = []
            nodo = actual
            while nodo is not None:
                camino.append(nodo)
                nodo = visitados.get(nodo)
            camino.reverse()
            
            caminos_encontrados[actual] = camino[1:]
            
            if len(caminos_encontrados) == vT:
                break

        x, y = actual
        
        for dx, dy in [(1,0), (-1,0), (0,1), (0,-1)]:
            nx, ny = x + dx, y + dy
            
            if 0 <= nx < filas and 0 <= ny < cols and grid[nx][ny] == 0:
                if (nx, ny) not in visitados:
                    cola.append((nx, ny))
                    visitados[(nx, ny)] = actual
    
    mejor_destino = None
    camino_mas_corto = []
    min_longitud = float('inf')
    
    for destino, camino in caminos_encontrados.items():
        if len(camino) < min_longitud:
            min_longitud = len(camino)
            mejor_destino = destino
            camino_mas_corto = camino
            
    return mejor_destino, camino_mas_corto