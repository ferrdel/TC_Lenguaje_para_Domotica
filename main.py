from lexer import Lexer
from parser_core import ParserDomotica

def ejecutar_analisis(codigo_prueba):
    print("--- INICIANDO FASE LÉXICA ---")
    try:
        lexer = Lexer(codigo_prueba)
        tokens = lexer.tokenizar()
        
        # Revisar si se acumularon errores durante la fase léxica
        if lexer.errores:
            print("\n[ERRORES LÉXICOS ENCONTRADOS]")
            for error in lexer.errores:
                print(f" - {error}")
            print("\n[PROCESO INTERRUMPIDO] Se aborta el paso a la fase sintáctica.")
            return
            
        for token in tokens:
            print(token)
            
        print("\n--- INICIANDO FASE SINTÁCTICA ---")
        parser = ParserDomotica(tokens)
        parser.parse_programa()
        
    except Exception as error:
        print(f"\n[PROCESO INTERRUMPIDO] {error}")

if __name__ == "__main__":
    codigo_domotica = """
    encender(luz_exterior);
    
    si (hora > 18) {
        encender(luces_sala);
        esperar(10);
    }
    
    repetir (3) {
        apagar(alarma);
    }
    """
    ejecutar_analisis(codigo_domotica)