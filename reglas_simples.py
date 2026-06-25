from ast_nodes import NodoComandoSimple

def parse_encender(parser):
    parser.consumir("ENCENDER")
    parser.consumir("PAREN_IZQ")
    
    parametro = parser.token_actual.valor if parser.token_actual else "desconocido"
    parser.consumir("IDENTIFICADOR")
    
    parser.consumir("PAREN_DER")
    parser.consumir("PUNTO_COMA")
    
    return NodoComandoSimple(accion="encender", parametro=parametro)

def parse_apagar(parser):
    parser.consumir("APAGAR")
    parser.consumir("PAREN_IZQ")
    
    parametro = parser.token_actual.valor if parser.token_actual else "desconocido"
    parser.consumir("IDENTIFICADOR")
    
    parser.consumir("PAREN_DER")
    parser.consumir("PUNTO_COMA")
    
    return NodoComandoSimple(accion="apagar", parametro=parametro)

def parse_esperar(parser):
    parser.consumir("ESPERAR")
    parser.consumir("PAREN_IZQ")
    
    parametro = parser.token_actual.valor if parser.token_actual else "0"
    parser.consumir("NUMERO")
    
    parser.consumir("PAREN_DER")
    parser.consumir("PUNTO_COMA")
    
    return NodoComandoSimple(accion="esperar", parametro=parametro)