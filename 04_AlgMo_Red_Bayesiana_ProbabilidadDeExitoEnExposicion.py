"""
=================================================================================
      SISTEMA DE INFERENCIA (BASADO EN RED BAYESIANA)          
=================================================================================
Dinámica del Algoritmo:
Una Red Bayesiana modela un problema usando un Grafo Dirigido Acíclico (DAG) 
donde los nodos son eventos probabilísticos y las flechas representan "causa y efecto".

A diferencia de la lógica tradicional (donde A = B), aquí usamos tablas de 
probabilidad condicional para manejar la incertidumbre del mundo real. 

En este caso práctico:
- Nodos: 'Estudio_Adecuado', 'Dominio_Tema', 'Exito_Exposicion'
- Relación: Estudiar causa el dominio del tema -> El dominio causa el éxito.
- Objetivo: El algoritmo genera una "distribución conjunta" (todas las 
  posibilidades del universo del problema) y nos permite hacer INFERENCIA.

Ejemplo de Inferencia (Razonamiento en reversa / Teorema de Bayes):
Si observamos el resultado final (ej. "La exposición fue un éxito"), la red 
puede calcular matemáticamente hacia atrás cuál es la probabilidad de que 
realmente hayas estudiado adecuadamente para lograrlo.
=================================================================================
"""

from typing import Dict, Tuple
import itertools
import matplotlib.pyplot as plt

# ---------------------------------------------------------
# 1. Definición de las variables y estructura de la red
# ---------------------------------------------------------
# Estructura causal (DAG): Estudio_Adecuado ──► Dominio_Tema ──► Exito_Exposicion

# Probabilidad inicial (A priori)
# P(Estudio_Adecuado)
P_Estudio: Dict[bool, float] = {
    True: 0.6,   # 60% de las veces el estudiante logra estudiar adecuadamente
    False: 0.4 
}

# Probabilidad Condicional: P(Dominio_Tema | Estudio_Adecuado)
P_Dominio_dado_Estudio: Dict[Tuple[bool, bool], float] = {
    # clave: (Dominio_Tema, Estudio_Adecuado)
    (True,  True): 0.85,  # Si estudia bien, 85% de probabilidad de dominar el tema
    (False, True): 0.15,  # 15% de veces estudia bien pero el tema es muy complejo

    (True,  False): 0.20, # Si no estudia, hay un 20% de probabilidad de que ya supiera el tema
    (False, False): 0.80
}

# Probabilidad Condicional: P(Exito_Exposicion | Dominio_Tema)
P_Exito_dado_Dominio: Dict[Tuple[bool, bool], float] = {
    # clave: (Exito_Exposicion, Dominio_Tema)
    (True,  True): 0.90,  # Si domina el tema, 90% de probabilidad de éxito en la exposición
    (False, True): 0.10,

    (True,  False): 0.30, # Si no domina el tema, 30% de éxito (buenas diapositivas/improvisación)
    (False, False): 0.70
}

def imprimir_tablas_locales():
    """ Imprime las Tablas de Probabilidad Condicional (CPDs) definidas """
    print("--- Tablas de Probabilidad Locales ---")
    print(" P(Estudio_Adecuado):")
    for v, p in P_Estudio.items():
        print(f"    P(Estudio={v}) = {p:.2f}")
    
    print("\n P(Dominio_Tema | Estudio_Adecuado):")
    print("    Estudio   Dominio   Probabilidad")
    for (dominio, estudio), prob in P_Dominio_dado_Estudio.items():
        print(f"    {estudio!s:7s}   {dominio!s:7s}   {prob:.2f}")
    
    print("\n P(Exito_Exposicion | Dominio_Tema):")
    print("    Dominio   Éxito     Probabilidad")
    for (exito, dominio), prob in P_Exito_dado_Dominio.items():
        print(f"    {dominio!s:7s}   {exito!s:7s}   {prob:.2f}")
    print("-" * 40 + "\n")

# ---------------------------------------------------------
# 2. Cálculo de la Probabilidad Conjunta
# ---------------------------------------------------------
def conjunta(estudio: bool, dominio: bool, exito: bool) -> float:
    """Calcula P(Estudio, Dominio, Exito) multiplicando las probabilidades locales."""
    pE = P_Estudio[estudio]
    pD = P_Dominio_dado_Estudio[(dominio, estudio)]
    pX = P_Exito_dado_Dominio[(exito, dominio)]
    return pE * pD * pX

todas_comb = list(itertools.product([True, False], repeat=3))

# ---------------------------------------------------------
# 3. Inferencias del Sistema Experto
# ---------------------------------------------------------
def marginal_exito_true() -> float:
    """ Inferencia hacia adelante: Calcula la probabilidad total de tener éxito """
    total = 0.0
    for (E, D, X) in todas_comb:
        if X is True:
            total += conjunta(E, D, X)
    return total

def posterior_estudio_dado_exito() -> float:
    """ 
    Inferencia diagnóstica (Bayes): Si sabemos que la exposición fue un éxito, 
    ¿cuál era la probabilidad de que el estudiante realmente haya estudiado?
    """
    num = 0.0
    den = 0.0
    for (E, D, X) in todas_comb:
        p = conjunta(E, D, X)
        if X is True:
            den += p          # Suma total de casos donde hubo éxito (Evidencia)
            if E is True:
                num += p      # Casos donde hubo éxito Y además se estudió

    return num / den

# ---------------------------------------------------------
# 4. Visualización del Grafo
# ---------------------------------------------------------
def dibujar_red_bayesiana():
    """ Dibuja la estructura causal de la red usando matplotlib """
    plt.figure(figsize=(8, 3))

    # Coordenadas de los nodos
    x_estudio, y_estudio = 0.1, 0.5
    x_dominio, y_dominio = 0.5, 0.5
    x_exito, y_exito = 0.9, 0.5

    # Cajas de texto para los nodos
    bbox_props = dict(boxstyle="round,pad=0.5", fc="#E0FFFF", ec="gray", lw=2)
    plt.text(x_estudio, y_estudio, "Estudio_Adecuado", ha='center', va='center', bbox=bbox_props, fontweight='bold')
    plt.text(x_dominio, y_dominio, "Dominio_Tema", ha='center', va='center', bbox=bbox_props, fontweight='bold')
    plt.text(x_exito, y_exito, "Exito_Exposicion", ha='center', va='center', bbox=dict(boxstyle="round,pad=0.5", fc="#98FB98", ec="gray", lw=2), fontweight='bold')

    # Flechas causales
    plt.annotate("", xy=(x_dominio-0.12, y_dominio), xytext=(x_estudio+0.12, y_estudio),
                 arrowprops=dict(arrowstyle="->", lw=2, color="gray"))
    
    plt.annotate("", xy=(x_exito-0.12, y_exito), xytext=(x_dominio+0.12, y_dominio),
                 arrowprops=dict(arrowstyle="->", lw=2, color="gray"))

    plt.xlim(0, 1)
    plt.ylim(0, 1)
    plt.axis('off')
    plt.title("Modelo Causal: Preparación de Exposición", pad=20, fontweight='bold')
    plt.tight_layout()
    plt.show()

def main():
    print("==============================================")
    print(" MOTOR DE INFERENCIA - RED BAYESIANA")
    print("==============================================\n")
    
    imprimir_tablas_locales()

    print("--- Análisis de Probabilidad Conjunta ---")
    suma_total = 0.0
    for (E, D, X) in todas_comb:
        p = conjunta(E, D, X)
        suma_total += p
        print(f" P(Estudio={str(E):<5}, Dominio={str(D):<5}, Exito={str(X):<5}) = {p:.5f}")
    
    print(f"\n Suma total del universo probabilístico = {suma_total:.1f}\n")

    # Ejecución de Inferencias
    p_exito = marginal_exito_true()
    p_estudio_si_exito = posterior_estudio_dado_exito()

    print("--- Resultados de Inferencia del Sistema ---")
    print("1. Predicción (Hacia adelante):")
    print(f"   Antes de presentar, la probabilidad general de éxito es: {p_exito*100:.1f}%")
    
    print("\n2. Diagnóstico (Hacia atrás / Teorema de Bayes):")
    print("   Evidencia observada: La exposición FUE UN ÉXITO.")
    print(f"   Conclusión: La probabilidad de que se haya estudiado adecuadamente es del {p_estudio_si_exito*100:.1f}%")
    print("==============================================\n")

    dibujar_red_bayesiana()

if __name__ == "__main__":
    main()