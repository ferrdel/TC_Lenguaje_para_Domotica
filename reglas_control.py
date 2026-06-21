def parse_condicional(parser):
    """Regla: si ( <identificador> <operador> <numero_o_id> ) { <lista_comandos> }"""
    parser.consumir("SI")
    parser.consumir("PAREN_IZQ")
    
    # Análisis de la condición
    var_condicion = parser.token_actual.valor if parser.token_actual else "?"
    parser.consumir("IDENTIFICADOR")
    
    operador = parser.token_actual.valor if parser.token_actual else "?"
    parser.consumir("OPERADOR")
    
    valor_comparacion = parser.token_actual.valor if parser.token_actual else "?"
    # El valor a comparar puede ser un número (ej: 24) o otra variable (ej: temp_max)
    if parser.token_actual and parser.token_actual.tipo == "NUMERO":
        parser.consumir("NUMERO")
    elif parser.token_actual and parser.token_actual.tipo == "IDENTIFICADOR":
        parser.consumir("IDENTIFICADOR")
    else:
        # Si no es ni número ni ID, forzamos un error descriptivo
        parser.consumir("NUMERO_O_IDENTIFICADOR")
        
    parser.consumir("PAREN_DER")
    print(f"[AST] Bloque de Control: Condicional -> si {var_condicion} {operador} {valor_comparacion}")
    
    # Inicio del anidamiento
    parser.consumir("LLAVE_IZQ")
    
    # ¡Llamada Recursiva! Delegamos al core para procesar el interior del bloque
    parser.parse_lista_comandos()
    
    # Fin del anidamiento
    parser.consumir("LLAVE_DER")
    print("[AST] Cierre de bloque condicional")


def parse_repeticion(parser):
    """Regla: repetir ( <numero> ) { <lista_comandos> }"""
    parser.consumir("REPETIR")
    parser.consumir("PAREN_IZQ")
    
    iteraciones = parser.token_actual.valor if parser.token_actual else "0"
    parser.consumir("NUMERO")
    
    parser.consumir("PAREN_DER")
    print(f"[AST] Bloque de Control: Bucle -> repetir {iteraciones} veces")
    
    # Inicio del anidamiento
    parser.consumir("LLAVE_IZQ")
    
    # ¡Llamada Recursiva!
    parser.parse_lista_comandos()
    
    # Fin del anidamiento
    parser.consumir("LLAVE_DER")
    print("[AST] Cierre de bloque repetición")