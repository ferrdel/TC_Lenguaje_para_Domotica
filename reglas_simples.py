from ast_nodes import NodoComandoSimple

# ==========================================
# [REGLA TERMINAL: ENCENDER] - ACTIVACIÓN DE HARDWARE
# ==========================================
def parse_encender(parser):
    """
    Analiza la producción gramatical para el comando de encendido.
    Estructura esperada: ENCENDER '(' IDENTIFICADOR ')' ';'
    """
    parser.consumir("ENCENDER")
    parser.consumir("PAREN_IZQ")
    
    # [EXTRACCIÓN DE CARGA ÚTIL]: Se captura el lexema (valor) del token actual 
    # antes de que la función consumir() lo descarte y avance el puntero.
    parametro = parser.token_actual.valor if parser.token_actual else "desconocido"
    parser.consumir("IDENTIFICADOR")
    
    parser.consumir("PAREN_DER")
    parser.consumir("PUNTO_COMA")
    
    # [INSTANCIACIÓN DEL AST]: Genera y retorna el nodo hoja correspondiente.
    return NodoComandoSimple(accion="encender", parametro=parametro)

# ==========================================
# [REGLA TERMINAL: APAGAR] - DESACTIVACIÓN DE HARDWARE
# ==========================================
def parse_apagar(parser):
    """
    Analiza la producción gramatical para el comando de apagado.
    Estructura esperada: APAGAR '(' IDENTIFICADOR ')' ';'
    """
    parser.consumir("APAGAR")
    parser.consumir("PAREN_IZQ")
    
    parametro = parser.token_actual.valor if parser.token_actual else "desconocido"
    parser.consumir("IDENTIFICADOR")
    
    parser.consumir("PAREN_DER")
    parser.consumir("PUNTO_COMA")
    
    return NodoComandoSimple(accion="apagar", parametro=parametro)

# ==========================================
# [REGLA TERMINAL: ESPERAR] - SUSPENSIÓN DE EJECUCIÓN (DELAY)
# ==========================================
def parse_esperar(parser):
    """
    Analiza la producción gramatical para el comando de espera/delay.
    Estructura esperada: ESPERAR '(' NUMERO ')' ';'
    """
    parser.consumir("ESPERAR")
    parser.consumir("PAREN_IZQ")
    
    # El parámetro capturado aquí corresponde a un valor numérico (tiempo).
    parametro = parser.token_actual.valor if parser.token_actual else "0"
    parser.consumir("NUMERO")
    
    parser.consumir("PAREN_DER")
    parser.consumir("PUNTO_COMA")
    
    return NodoComandoSimple(accion="esperar", parametro=parametro)