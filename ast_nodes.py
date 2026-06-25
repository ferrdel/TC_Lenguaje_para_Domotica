from dataclasses import dataclass, field
from typing import List

# ==========================================
# CLASE BASE
# ==========================================
@dataclass
class NodoAST:
    """Clase padre genérica para todos los nodos del árbol."""
    pass

# ==========================================
# NODO RAÍZ (El tronco del árbol)
# ==========================================
@dataclass
class NodoPrograma(NodoAST):
    """Contiene la lista principal de todos los comandos del script."""
    comandos: List[NodoAST] = field(default_factory=list)

# ==========================================
# NODOS HOJA (Comandos de una línea)
# ==========================================
@dataclass
class NodoComandoSimple(NodoAST):
    """Maneja las acciones directas: encender, apagar, esperar."""
    accion: str      # ej: "encender", "apagar", "esperar"
    parametro: str   # ej: "luz_sala", "aire_acondicionado", "10"

# ==========================================
# NODOS RAMA (Bloques con código adentro)
# ==========================================
@dataclass
class NodoCondicional(NodoAST):
    """Maneja la estructura de control 'si'."""
    variable: str           # ej: "temp"
    operador: str           # ej: ">"
    valor_comparacion: str  # ej: "24"
    bloque: List[NodoAST] = field(default_factory=list) # Los comandos que van entre las llaves

@dataclass
class NodoRepeticion(NodoAST):
    """Maneja la estructura de control 'repetir'."""
    iteraciones: str        # ej: "3"
    bloque: List[NodoAST] = field(default_factory=list) # Los comandos que van entre las llaves