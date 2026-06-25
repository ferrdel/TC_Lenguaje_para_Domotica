from ast_nodes import NodoCondicional, NodoRepeticion

def parse_condicional(parser):
    parser.consumir("SI")
    parser.consumir("PAREN_IZQ")
    
    variable = parser.token_actual.valor if parser.token_actual else ""
    parser.consumir("IDENTIFICADOR")
    
    operador = parser.token_actual.valor if parser.token_actual else ""
    # Mantenemos la etiqueta correcta para tu Lexer
    parser.consumir("OPERADOR") 
    
    # --- SINTAXIS PURA: Aceptamos número o identificador sin importar la coherencia de tipos ---
    valor_comparacion = parser.token_actual.valor if parser.token_actual else ""
    if parser.token_actual and parser.token_actual.tipo == "NUMERO":
        parser.consumir("NUMERO")
    elif parser.token_actual and parser.token_actual.tipo == "IDENTIFICADOR":
        parser.consumir("IDENTIFICADOR")
    else:
        # Si llega acá, es porque pusieron otra cosa (ej: un símbolo). Tira error sintáctico puro.
        parser.consumir("NUMERO_O_IDENTIFICADOR") 
    
    parser.consumir("PAREN_DER")
    parser.consumir("LLAVE_IZQ")
    
    bloque = parser.parse_lista_comandos()
    
    parser.consumir("LLAVE_DER")
    
    return NodoCondicional(variable=variable, operador=operador, valor_comparacion=valor_comparacion, bloque=bloque)

def parse_repeticion(parser):
    parser.consumir("REPETIR")
    parser.consumir("PAREN_IZQ")
    
    iteraciones = parser.token_actual.valor if parser.token_actual else "0"
    parser.consumir("NUMERO")
    
    parser.consumir("PAREN_DER")
    parser.consumir("LLAVE_IZQ")
    
    bloque = parser.parse_lista_comandos()
    
    parser.consumir("LLAVE_DER")
    
    return NodoRepeticion(iteraciones=iteraciones, bloque=bloque)
def parse_repeticion(parser):
    parser.consumir("REPETIR")
    parser.consumir("PAREN_IZQ")
    
    iteraciones = parser.token_actual.valor if parser.token_actual else "0"
    parser.consumir("NUMERO")
    
    parser.consumir("PAREN_DER")
    parser.consumir("LLAVE_IZQ")
    
    bloque = parser.parse_lista_comandos()
    
    parser.consumir("LLAVE_DER")
    
    return NodoRepeticion(iteraciones=iteraciones, bloque=bloque)