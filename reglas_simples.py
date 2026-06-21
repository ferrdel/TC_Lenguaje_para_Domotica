def parse_encender(parser):
    """Regla: <comando> -> encender ( <identificador> ) ;"""
    parser.consumir("ENCENDER")
    parser.consumir("PAREN_IZQ")
    
    # Capturamos el nombre del dispositivo antes de avanzar el puntero
    id_dispositivo = parser.token_actual.valor if parser.token_actual else "desconocido"
    parser.consumir("IDENTIFICADOR")
    
    parser.consumir("PAREN_DER")
    parser.consumir("PUNTO_COMA")
    
    # Simulación de generación de código / AST
    print(f"[AST] Comando válido: Encender dispositivo -> '{id_dispositivo}'")


def parse_apagar(parser):
    """Regla: <comando> -> apagar ( <identificador> ) ;"""
    parser.consumir("APAGAR")
    parser.consumir("PAREN_IZQ")
    
    id_dispositivo = parser.token_actual.valor if parser.token_actual else "desconocido"
    parser.consumir("IDENTIFICADOR")
    
    parser.consumir("PAREN_DER")
    parser.consumir("PUNTO_COMA")
    
    print(f"[AST] Comando válido: Apagar dispositivo -> '{id_dispositivo}'")


def parse_esperar(parser):
    """Regla: <comando> -> esperar ( <numero> ) ;"""
    parser.consumir("ESPERAR")
    parser.consumir("PAREN_IZQ")
    
    # Capturamos los segundos (esperamos un token de tipo NUMERO)
    tiempo = parser.token_actual.valor if parser.token_actual else "0"
    parser.consumir("NUMERO")
    
    parser.consumir("PAREN_DER")
    parser.consumir("PUNTO_COMA")
    
    print(f"[AST] Comando válido: Esperar -> {tiempo} segundos")