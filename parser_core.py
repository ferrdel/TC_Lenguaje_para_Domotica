import reglas_simples
import reglas_control
from ast_nodes import NodoPrograma

# ==========================================
# EXCEPCIÓN DE CONTROL DE FLUJO
# ==========================================
class ErrorSincronizacion(Exception):
    """
    Excepción utilizada para el desenrollado de la pila (Stack Unwinding).
    Permite abortar inmediatamente la ejecución de una regla gramatical rota
    y delegar el control al mecanismo de recuperación de errores en modo pánico.
    """
    pass

# ==========================================
# ANALIZADOR SINTÁCTICO PRINCIPAL (PARSER)
# ==========================================
class ParserDomotica:
    def __init__(self, lista_tokens):
        """
        Inicializa el estado del autómata sintáctico.
        Mantiene el flujo de tokens, el puntero de preanálisis (Lookahead),
        el registro centralizado de fallos y el objeto raíz del AST.
        """
        self.tokens = lista_tokens
        self.posicion = 0
        self.token_actual = self.tokens[self.posicion] if self.tokens else None
        self.errores = [] 
        self.arbol_ast = None # Almacenamiento en memoria del AST para la capa de presentación (Streamlit)

    def avanzar(self):
        """
        Avanza el puntero de preanálisis un elemento hacia adelante en el flujo de tokens.
        Controla el fin de archivo asignando un valor nulo (None) al alcanzar el límite.
        """
        self.posicion += 1
        if self.posicion < len(self.tokens):
            self.token_actual = self.tokens[self.posicion]
        else:
            self.token_actual = None

    def sincronizar(self):
        """
        Estrategia de recuperación en Modo Pánico.
        Descarta tokens secuencialmente hasta encontrar un 'Token de Sincronización' (Ancla),
        reestabilizando el estado del parser para continuar analizando las sentencias subsiguientes.
        """
        tokens_seguros = ["PUNTO_COMA", "LLAVE_DER", "LLAVE_IZQ"]
        while self.token_actual and self.token_actual.tipo not in tokens_seguros:
            self.avanzar()
            
        # Si la sincronización se detuvo en un delimitador de línea, se consume para limpiar la expresión.
        if self.token_actual and self.token_actual.tipo == "PUNTO_COMA":
            self.avanzar()

    def consumir(self, tipo_esperado):
        """
        Valida que el token de preanálisis (Lookahead) coincida con el componente léxico
        esperado por la gramática. Si coincide, avanza; de lo contrario, registra la violación
        e interrumpe el flujo mediante la excepción de sincronización.
        """
        if self.token_actual and self.token_actual.tipo == tipo_esperado:
            self.avanzar()
        else:
            encontrado = self.token_actual.tipo if self.token_actual else "FIN_DE_ARCHIVO"
            linea = self.token_actual.linea if self.token_actual else "desconocida"
            col = self.token_actual.columna if self.token_actual else "desconocida"
            
            # Registro formal de desviación sintáctica real
            self.errores.append({
                "tipo": "Real",
                "mensaje": f"Error Sintáctico [L:{linea}, C:{col}]: Se esperaba '{tipo_esperado}', pero se encontró '{encontrado}'"
            })
            raise ErrorSincronizacion()

    def parse_programa(self):
        """
        Punto de entrada principal del Analizador Sintáctico.
        Inicia la derivación del axioma inicial de la gramática y encapsula la
        lista resultante de sub-nodos en el nodo raíz global.
        """
        lista_final_nodos = self.parse_lista_comandos()
        
        # Validación de residuos flotantes posteriores al alcance lógico de la gramática.
        if self.token_actual is not None:
            self.errores.append({
                "tipo": "Consecuencia",
                "mensaje": f"Efecto Colateral [L:{self.token_actual.linea}]: Símbolo '{self.token_actual.valor}' huérfano al final del archivo"
            })
            
        # Instanciación y almacenamiento del objeto raíz definitivo
        self.arbol_ast = NodoPrograma(comandos=lista_final_nodos)
        return self.arbol_ast

    def parse_lista_comandos(self):
        """
        Evalúa secuencias repetitivas de sentencias mediante recursividad por la derecha.
        Determina la bifurcación del flujo basándose en la pertenencia del token actual al Conjunto de Selección.
        """
        lista_nodos = []
        # CONJUNTO DE SELECCIÓN (FIRST SET): Tokens válidos para iniciar un comando
        first_comando = ["ENCENDER", "APAGAR", "ESPERAR", "SI", "REPETIR"]
        
        # Condición de parada formal: fin de flujo o cierre de bloque subordinado
        if not self.token_actual or self.token_actual.tipo == "LLAVE_DER":
            return lista_nodos
            
        if self.token_actual.tipo in first_comando:
            nodo = self.parse_comando()
            if nodo:
                lista_nodos.append(nodo)
            # Extensión recursiva de la lista de nodos sintácticos
            lista_nodos.extend(self.parse_lista_comandos())
        else:
            # Captura de error sintáctico directo por token fuera del Conjunto de Selección
            self.errores.append({
                "tipo": "Real",
                "mensaje": f"Error Sintáctico [L:{self.token_actual.linea}]: Instrucción no válida '{self.token_actual.valor}'. Se esperaba un comando (encender, apagar, si, esperar, repetir)."
            })
            
            # Resguardo preventivo para evitar bucles infinitos durante la descompresión del error
            token_antes = self.token_actual
            self.sincronizar()
            if self.token_actual == token_antes:
                self.avanzar()
                
            lista_nodos.extend(self.parse_lista_comandos())
            
        return lista_nodos

    def parse_comando(self):
        """
        Enrutador principal (Dispatcher) del análisis predictivo.
        Deriva el control de análisis hacia las sub-reglas específicas según el token de Lookahead.
        Encapsula las llamadas en un bloque try-except para aislar y contener fallos de sincronización.
        """
        if not self.token_actual:
            return None
            
        tipo = self.token_actual.tipo
        nodo = None
        
        try:
            if tipo == "ENCENDER":
                nodo = reglas_simples.parse_encender(self)
            elif tipo == "APAGAR":
                nodo = reglas_simples.parse_apagar(self)
            elif tipo == "ESPERAR":
                nodo = reglas_simples.parse_esperar(self)
            elif tipo == "SI":
                nodo = reglas_control.parse_condicional(self)
            elif tipo == "REPETIR":
                nodo = reglas_control.parse_repeticion(self)
            else:
                self.errores.append({
                    "tipo": "Real",
                    "mensaje": f"Error Sintáctico [L:{self.token_actual.linea}]: Comando no reconocido '{tipo}'"
                })
                self.sincronizar()
                
        except ErrorSincronizacion:
            # Captura el desenrollado provocado por 'consumir()' e inicia el aislamiento en la regla actual
            self.sincronizar()
            
        return nodo