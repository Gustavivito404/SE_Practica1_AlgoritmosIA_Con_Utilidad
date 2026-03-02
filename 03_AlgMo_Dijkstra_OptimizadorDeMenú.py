"""
=================================================================================
      OPTIMIZADOR DE MENÚ (ESTRUCTURA DE RED NEURONAL MULTICAPA)          
=================================================================================
Dinámica del Algoritmo:
Se modela el problema como un grafo dirigido estructurado en capas (fully connected).
- Nodos: Platillos disponibles.
- Capas: Tiempos de la comida (Inicio -> Entradas -> Principal -> Bebidas -> Fin).
- Pesos: El precio exacto del platillo de destino.

El algoritmo de Dijkstra evaluará todas las combinaciones posibles atravesando
las capas para encontrar la secuencia de platillos que resulte en la cuenta
total más económica.
=================================================================================
"""

import heapq
import networkx as nx
import matplotlib.pyplot as plt
import math

def imprimir_tabla(distances, visited, previous):
    """ Imprime el estado actual de los costos y caminos calculados. """
    print("\nTabla actual de costos acumulados:")
    print("{:<15} {:<12} {:<10} {:<15}".format("Platillo", "Costo Total", "Evaluado", "Plato Previo"))
    print("-" * 55)
    for node in sorted(distances.keys()):
        dist = distances[node]
        dist_str = "∞" if dist == math.inf else f"${dist:.1f}"
        vis_str = "Sí" if node in visited else "No"
        prev_str = previous[node] if previous[node] is not None else "-"
        print("{:<15} {:<12} {:<10} {:<15}".format(node, dist_str, vis_str, prev_str))
    print("-" * 55)

def dijkstra_paso_a_paso(graph, start):
    """
    Ejecuta Dijkstra imprimiendo la toma de decisiones para encontrar 
    la combinación de platillos más económica.
    """
    distances = {node: float("inf") for node in graph}
    distances[start] = 0
    previous = {node: None for node in graph}

    priority_queue = [(0, start)]
    visited = set()
    paso = 0

    print("\n=== INICIO DE BÚSQUEDA DE RUTA MÁS BARATA (DIJKSTRA) ===")
    
    while priority_queue:
        paso += 1
        current_dist, current_node = heapq.heappop(priority_queue)

        if current_dist > distances[current_node]:
            continue

        visited.add(current_node)

        # Evaluar el costo de los platillos en la siguiente capa
        for neighbor, weight in graph[current_node].items():
            distance = current_dist + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                previous[neighbor] = current_node
                heapq.heappush(priority_queue, (distance, neighbor))

    imprimir_tabla(distances, visited, previous)
    print("\n=== FIN DE LA BÚSQUEDA ===")
    return distances, previous

def reconstruir_camino(previous, start, goal):
    """ Traza la ruta óptima de regreso desde el destino hasta el origen. """
    if goal not in previous or (previous[goal] is None and goal != start):
        return None

    path = []
    nodo = goal

    while nodo is not None:
        path.append(nodo)
        if nodo == start:
            break
        nodo = previous[nodo]

    path.reverse()
    return path

def dibujar_grafo_menu(graph, capas, shortest_path=None):
    """ Visualiza el grafo emulando la estructura de una red neuronal. """
    G = nx.DiGraph() 

    for node, neighbors in graph.items():
        for neighbor, weight in neighbors.items():
            G.add_edge(node, neighbor, weight=weight)
    
    # Asignar a cada nodo la capa a la que pertenece para el layout
    for i, capa in enumerate(capas):
        for nodo in capa:
            if nodo in G.nodes():
                G.nodes[nodo]["layer"] = i

    pos = nx.multipartite_layout(G, subset_key="layer")

    path_edges = set()
    if shortest_path is not None:
        for u, v in zip(shortest_path[:-1], shortest_path[1:]):
            path_edges.add((u, v))

    edge_colors = []
    edge_widths = []
    for u, v in G.edges():
        if (u, v) in path_edges:
            edge_colors.append("red")
            edge_widths.append(3.0)
        else:
            edge_colors.append("#E0E0E0") # Gris muy claro para no saturar
            edge_widths.append(0.5)

    node_colors = []
    if shortest_path is not None:
        path_nodes = set(shortest_path)
        for node in G.nodes():
            if node == shortest_path[0]:
                node_colors.append("#98FB98") 
            elif node == shortest_path[-1]:
                node_colors.append("#FFB6C1") 
            elif node in path_nodes:
                node_colors.append("#FFD700") 
            else:
                node_colors.append("#ADD8E6") 
    else:
        node_colors = ["#ADD8E6"] * len(G.nodes())

    plt.figure(figsize=(14, 8))
    nx.draw_networkx(
        G, pos, with_labels=True, node_color=node_colors,
        edge_color=edge_colors, width=edge_widths,
        node_size=2500, font_size=9, font_weight="bold", arrows=True, arrowsize=10
    )

    # Solo dibujamos los pesos de la ruta óptima para no saturar visualmente
    # una gráfica totalmente conectada
    edge_labels = nx.get_edge_attributes(G, "weight")
    path_labels = {edge: edge_labels[edge] for edge in path_edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=path_labels, font_size=10, font_color="red")

    plt.title("Ruta Óptima de Menú (Topología de Red Neuronal)")
    plt.axis("off")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    # 1. Definimos las capas como en una red neuronal
    capas_menu = [
        ["Ensalada"],                                   # Capa 0: Inicio
        ["Sopa", "Crema", "Empanada"],                  # Capa 1: Entradas
        ["Pollo", "Carne", "Pescado", "Pasta"],         # Capa 2: Plato Principal
        ["Refresco", "Cerveza", "Vino", "Limonada"],    # Capa 3: Bebidas
        ["Cafe"]                                        # Capa 4: Fin
    ]

    # 2. Diccionario global de precios
    precios = {
        "Ensalada": 0, "Sopa": 40, "Crema": 45, "Empanada": 35,
        "Pollo": 90, "Carne": 120, "Pescado": 110, "Pasta": 80,
        "Refresco": 25, "Cerveza": 40, "Vino": 60, "Limonada": 30,
        "Cafe": 20
    }

    # 3. Construimos el grafo conectando todas las capas secuencialmente
    menu_graph = {}
    for i in range(len(capas_menu) - 1):
        for origen in capas_menu[i]:
            if origen not in menu_graph:
                menu_graph[origen] = {}
            for destino in capas_menu[i+1]:
                # El peso de la arista es el precio del platillo destino
                menu_graph[origen][destino] = precios[destino]
    menu_graph["Cafe"] = {} # Nodo final sin salidas

    origen = "Ensalada"
    destino = "Cafe"

    print(f"Buscando la ruta más económica desde '{origen}' hasta '{destino}'...\n")

    distances, previous = dijkstra_paso_a_paso(menu_graph, origen)
    shortest_path = reconstruir_camino(previous, origen, destino)

    print("\n===================================================")
    if shortest_path is None:
        print(f"No hay una secuencia válida para llegar de {origen} a {destino}.")
    else:
        print(f"ORDEN SUGERIDO (Camino más barato):")
        print(" -> ".join(shortest_path))
        print(f"\nCuenta Total Estimada: ${distances[destino]:.2f}")
    print("===================================================")

    dibujar_grafo_menu(menu_graph, capas_menu, shortest_path)
