from dataclasses import dataclass, field
from typing import List

# ==========================================
# CLASE BASE ABSTRACTA
# ==========================================
@dataclass
class NodoAST:
    """
    Clase base para el polimorfismo del Árbol de Sintaxis Abstracta (AST).
    Todos los nodos heredan de esta estructura para facilitar el tipado estático
    y los recorridos recursivos.
    """
    pass

# ==========================================
# NODO RAÍZ (Punto de entrada)
# ==========================================
@dataclass
class NodoPrograma(NodoAST):
    """
    Representa el nodo raíz del AST. 
    Actúa como contenedor global de la secuencia de sentencias ejecutables del script.
    """
    comandos: List[NodoAST] = field(default_factory=list)

# ==========================================
# NODOS HOJA (Operaciones Atómicas)
# ==========================================
@dataclass
class NodoComandoSimple(NodoAST):
    """
    Representa instrucciones terminales que no contienen bloques anidados.
    Maneja las acciones de hardware directo (ej: encender, apagar) o del sistema (esperar).
    """
    accion: str      # Identificador de la instrucción (ej: "encender")
    parametro: str   # Argumento pasado a la instrucción (ej: "luz_patio")

# ==========================================
# NODOS RAMA (Estructuras de Control de Flujo)
# ==========================================
@dataclass
class NodoCondicional(NodoAST):
    """
    Representa una bifurcación de control de flujo basada en una expresión relacional.
    Almacena los operandos, el operador y el bloque de sentencias subordinadas.
    """
    variable: str           # Operando izquierdo (ej: "hora")
    operador: str           # Operador relacional (ej: ">", "==")
    valor_comparacion: str  # Operando derecho (ej: "18")
    bloque: List[NodoAST] = field(default_factory=list) # Cuerpo del condicional

@dataclass
class NodoRepeticion(NodoAST):
    """
    Representa una estructura iterativa de ciclo acotado.
    Define la cantidad de iteraciones estáticas y encapsula el bloque de código a repetir.
    """
    iteraciones: str        # Límite del ciclo (ej: "3")
    bloque: List[NodoAST] = field(default_factory=list) # Cuerpo del ciclo