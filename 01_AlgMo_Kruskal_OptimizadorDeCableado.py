# Optimizador de Cableado de Red usando el algoritmo de Kruskal

import networkx as nx
import matplotlib.pyplot as plt

def construir_red_dispositivos():
    """ 
    Construye la gráfica ponderada. 
    Nodos = dispositivos, Pesos = metros de cable. 
    """
    G = nx.Graph()
    # Se definen las conexiones posibles y sus respectivas distancias
    G.add_weighted_edges_from([
        ('Router', 'PC_Estudio', 10), ('Router', 'TV_Sala', 15),
        ('Router', 'Raspberry_Pi', 12), ('PC_Estudio', 'Impresora_3D', 2),
        ('PC_Estudio', 'Servidor_NAS', 3), ('TV_Sala', 'Servidor_NAS', 8),
        ('TV_Sala', 'Consola', 1), ('Servidor_NAS', 'Raspberry_Pi', 6),
        ('Impresora_3D', 'Raspberry_Pi', 14), ('Consola', 'Router', 16)
    ])
    return G

class UnionFind:
    """ 
    Estructura Union-Find para manejar los conjuntos de nodos conectados 
    y evitar la formación de ciclos al agregar cables. 
    """
    def __init__(self, elementos):
        # Inicialmente, cada dispositivo es su propio componente (padre de sí mismo)
        self.parent = {x: x for x in elementos}
        # El rango ayuda a mantener el árbol balanceado al hacer uniones
        self.rank = {x: 0 for x in elementos}

    def find(self, x):
        # Búsqueda con compresión de caminos: hace que los nodos apunten directamente a la raíz
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, a, b):
        # Encuentra las raíces de los componentes a los que pertenecen 'a' y 'b'
        raiz_a = self.find(a)
        raiz_b = self.find(b)

        # Si tienen la misma raíz, ya están en la misma red (formaría un ciclo)
        if raiz_a == raiz_b:
            return False

        # Unión por rango: el árbol con menor profundidad se une a la raíz del más profundo
        if self.rank[raiz_a] < self.rank[raiz_b]:
            self.parent[raiz_a] = raiz_b
        elif self.rank[raiz_a] > self.rank[raiz_b]:
            self.parent[raiz_b] = raiz_a
        else:
            # Si tienen la misma profundidad, se elige uno como raíz y se incrementa su rango
            self.parent[raiz_b] = raiz_a
            self.rank[raiz_a] += 1
        return True

def optimizar_cableado(G):
    """ 
    Encuentra el Árbol de Expansión Mínima (MST) iterando sobre las aristas. 
    """
    print("--- Planificador de Cableado LAN (Kruskal) ---\n")

    # Paso 1: Ordenar todas las posibles conexiones de menor a mayor distancia
    aristas = sorted(G.edges(data=True), key=lambda e: e[2]['weight'])

    # Inicializar la estructura para rastrear las conexiones y las variables de control
    uf = UnionFind(G.nodes())
    mst_edges = []
    metros_totales = 0

    print("Proceso de conexión:")
    # Paso 2: Evaluar cada conexión previamente ordenada
    for (u, v, data) in aristas:
        peso = data['weight']
        
        # Paso 3: Intentar unir los nodos. Si el método retorna True, no hay ciclo.
        if uf.union(u, v):
            mst_edges.append((u, v, peso))
            metros_totales += peso
            print(f"Agregado: {u} - {v} ({peso}m)")
            
            # Condición de paro: un árbol de 'n' nodos se completa con 'n-1' aristas
            if len(mst_edges) == len(G.nodes()) - 1:
                break
        else:
            # Si retorna False, los nodos ya tenían un camino entre ellos
            print(f"Descartado: {u} - {v} ({peso}m) - Ciclo detectado")
            
    print("\n--- Resumen de Instalación ---")
    print(f"Total de cable requerido: {metros_totales}m\n")

    return mst_edges

def main():
    # 1. Construcción del modelo de red base
    G = construir_red_dispositivos()
    
    # 2. Ejecución del algoritmo para obtener las conexiones finales
    conexion_optima = optimizar_cableado(G)

    # 3. Creación de un nuevo grafo solo con las conexiones óptimas para visualizarlo
    H_optima = nx.Graph()
    H_optima.add_weighted_edges_from(conexion_optima)

    # Generación de coordenadas espaciales fijas para que los gráficos coincidan visualmente
    pos = nx.spring_layout(G, seed=42)
    
    # Extracción de las etiquetas (pesos) para mostrarlas en los enlaces
    labels_full = nx.get_edge_attributes(G, "weight")
    labels_optima = nx.get_edge_attributes(H_optima, "weight")

    # Configuración de la figura con dos subgráficos lado a lado
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Renderizado del primer gráfico (Todas las conexiones)
    axes[0].set_title("Conexiones posibles")
    nx.draw(G, pos=pos, ax=axes[0], with_labels=True, node_color="#87CEEB", node_size=2500, font_size=9)
    nx.draw_networkx_edge_labels(G, pos, ax=axes[0], edge_labels=labels_full)

    # Renderizado del segundo gráfico (Solo el cableado óptimo)
    axes[1].set_title("Cableado Óptimo (Kruskal)")
    nx.draw(H_optima, pos=pos, ax=axes[1], with_labels=True, node_color="#98FB98", node_size=2500, font_size=9)
    nx.draw_networkx_edge_labels(H_optima, pos, ax=axes[1], edge_labels=labels_optima)

    # Ajuste de márgenes y visualización final
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()