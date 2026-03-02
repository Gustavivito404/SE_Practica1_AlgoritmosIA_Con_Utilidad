"""
=================================================================================
      PLANIFICADOR DE FLUJO DE TRABAJO (BASADO EN EL ALGORITMO DE PRIM)          
=================================================================================
Dinámica del Algoritmo:
Construye un 'Árbol de Expansión Mínima', conectando todos los elementos de la 
forma más eficiente posible sin formar ciclos.

En este caso práctico:
- Los NODOS representan las tareas a realizar.
- Los PESOS representan el 'Costo de Cambio de Contexto' (en minutos).

Ejemplo de Cambio de Contexto:
Si estás programando y pasas a otra tarea de programación similar (ej. crear
un espacio de trabajo a programar un nodo), el tiempo de adaptación mental es
bajo. Sin embargo, si saltas de programar a estudiar teoría pura, tu cerebro
tarda mucho más en ajustar el enfoque y preparar los nuevos materiales.

Objetivo:
El programa enlazará todas tus tareas partiendo de una inicial, sugiriendo
siempre saltar a la tarea más afín a las que ya tienes activas, minimizando
el tiempo muerto o la fricción mental en tus transiciones.
=================================================================================
"""

import networkx as nx
import matplotlib.pyplot as plt

def construir_red_tareas():
    """ 
    Construye la red de tareas del proyecto. 
    Nodos = Tareas a realizar.
    Pesos = Minutos de 'tiempo de transición' o esfuerzo mental.
    """
    G = nx.Graph()
    G.add_weighted_edges_from([
        ('Instalar_ROS2', 'Crear_Workspace', 15),
        ('Crear_Workspace', 'Nodo_Publicador', 20),
        ('Nodo_Publicador', 'Nodo_Cinematica', 10),
        ('Nodo_Cinematica', 'Simulacion_2DOF', 25),
        ('Instalar_ROS2', 'Expo_Sistemas_Expertos', 60), 
        ('Expo_Sistemas_Expertos', 'Investigacion_Reglas', 15),
        ('Simulacion_2DOF', 'Expo_Sistemas_Expertos', 45),
        ('Crear_Workspace', 'Investigacion_Reglas', 50),
        ('Nodo_Publicador', 'Instalar_ROS2', 30)
    ])
    return G

def prim_flujo_trabajo(G):
    """ 
    Implementación de Prim para encontrar el flujo de tareas 
    que minimice los tiempos de transición.
    """
    print("--- Generando Ruta de Flujo de Trabajo Óptimo ---")
    
    limite = float('inf')

    # A: Diccionario de tareas pendientes. Formato: A[tarea] = (tarea_previa, tiempo_transicion)
    A = {v: (None, limite) for v in G.nodes}
    
    # Seleccionamos la primera tarea del grafo como punto de arranque
    tarea_inicial = list(A.keys())[0]
    del A[tarea_inicial]

    transiciones_optimas = []
    tiempo_perdido_total = 0
    print(f"Iniciando jornada con: {tarea_inicial}")

    # Evaluar el costo de pasar a las tareas relacionadas directamente
    for v in G.neighbors(tarea_inicial):
        A[v] = (tarea_inicial, G[v][tarea_inicial]['weight'])

    paso = 1
    # Mientras existan tareas pendientes de agregar al flujo
    while A:
        mejor_tiempo = limite
        siguiente_tarea = None
        
        # Buscar la tarea pendiente que requiera el menor tiempo de transición
        for v in A.keys():
            if A[v][1] < mejor_tiempo:
                siguiente_tarea = v
                mejor_tiempo = A[v][1]

        tarea_origen, tiempo = A[siguiente_tarea]
        transiciones_optimas.append((tarea_origen, siguiente_tarea, tiempo))
        tiempo_perdido_total += tiempo
        
        print(f"Paso {paso}: De '{tarea_origen}' es más eficiente pasar a '{siguiente_tarea}' ({tiempo} min de transición)")
        paso += 1

        # Marcar la tarea como integrada al flujo
        del A[siguiente_tarea]

        # Actualizar los tiempos de transición para las tareas restantes
        for v in G.neighbors(siguiente_tarea):
            if v in A:
                w = G[v][siguiente_tarea]['weight']
                # Si transicionar desde la nueva tarea es más rápido, se actualiza la ruta propuesta
                if w < A[v][1]:
                    A[v] = (siguiente_tarea, w)

    print(f"\nTiempo total estimado en transiciones: {tiempo_perdido_total} minutos")
    return transiciones_optimas

def main():
    G = construir_red_tareas()

    # Ejecutar Prim para obtener el árbol de transiciones mínimas
    mst_edges = prim_flujo_trabajo(G)
    H = nx.Graph()
    H.add_weighted_edges_from(mst_edges)

    # Configuración de los diagramas
    pos = nx.spring_layout(G, seed=42)
    labels_full = nx.get_edge_attributes(G, 'weight')
    labels_mst = nx.get_edge_attributes(H, 'weight')

    fig, ax = plt.subplots(1, 2, figsize=(15, 6))

    ax[0].set_title("Relación de Tareas y Tiempos de Transición (Grafo Original)")
    nx.draw(G, pos=pos, ax=ax[0], with_labels=True, node_color="#D3D3D3", node_size=2200, font_size=8)
    nx.draw_networkx_edge_labels(G, pos, ax=ax[0], edge_labels=labels_full)

    ax[1].set_title("Flujo de Trabajo Sugerido (Prim)")
    nx.draw(H, pos=pos, ax=ax[1], with_labels=True, node_color="#ADD8E6", node_size=2200, font_size=8)
    nx.draw_networkx_edge_labels(H, pos, ax=ax[1], edge_labels=labels_mst)

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()