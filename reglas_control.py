from ast_nodes import NodoCondicional, NodoRepeticion

# ==========================================
# [REGLA NO TERMINAL: SI] - BIFURCACIÓN CONDICIONAL
# ==========================================
def parse_condicional(parser):
    """
    Analiza la producción gramatical para la estructura de control 'si'.
    Estructura esperada: SI '(' IDENTIFICADOR OPERADOR (NUMERO | IDENTIFICADOR) ')' '{' BLOQUE '}'
    """
    parser.consumir("SI")
    parser.consumir("PAREN_IZQ")
    
    variable = parser.token_actual.valor if parser.token_actual else ""
    parser.consumir("IDENTIFICADOR")
    
    operador = parser.token_actual.valor if parser.token_actual else ""
    parser.consumir("OPERADOR") 
    
    # [EVALUACIÓN SINTÁCTICA PURA]: Gramática Libre de Contexto.
    # Aceptamos identificadores o números en el lado derecho de la comparación
    # delegando la validación de coherencia de tipos al Analizador Semántico.
    valor_comparacion = parser.token_actual.valor if parser.token_actual else ""
    if parser.token_actual and parser.token_actual.tipo == "NUMERO":
        parser.consumir("NUMERO")
    elif parser.token_actual and parser.token_actual.tipo == "IDENTIFICADOR":
        parser.consumir("IDENTIFICADOR")
    else:
        # Forzamos el error sintáctico si el token no pertenece a los tipos válidos
        parser.consumir("NUMERO_O_IDENTIFICADOR") 
    
    parser.consumir("PAREN_DER")
    parser.consumir("LLAVE_IZQ")
    
    # [RECURSIVIDAD INDIRECTA]: Llamada al motor para procesar sentencias anidadas
    bloque = parser.parse_lista_comandos()
    
    parser.consumir("LLAVE_DER")
    
    # [INSTANCIACIÓN DEL AST]: Retorna el nodo rama conteniendo sus bloques hijos
    return NodoCondicional(variable=variable, operador=operador, valor_comparacion=valor_comparacion, bloque=bloque)

# ==========================================
# [REGLA NO TERMINAL: REPETIR] - BUCLE ITERATIVO
# ==========================================
def parse_repeticion(parser):
    """
    Analiza la producción gramatical para la estructura iterativa 'repetir'.
    Estructura esperada: REPETIR '(' NUMERO ')' '{' BLOQUE '}'
    """
    parser.consumir("REPETIR")
    parser.consumir("PAREN_IZQ")
    
    iteraciones = parser.token_actual.valor if parser.token_actual else "0"
    parser.consumir("NUMERO")
    
    parser.consumir("PAREN_DER")
    parser.consumir("LLAVE_IZQ")
    
    # [RECURSIVIDAD INDIRECTA]: Poblando el cuerpo del bucle
    bloque = parser.parse_lista_comandos()
    
    parser.consumir("LLAVE_DER")
    
    return NodoRepeticion(iteraciones=iteraciones, bloque=bloque)