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
    # Código de prueba simple de domótica
    codigo_domotica = """
    encender(luz_sala);
    esperar(30);
    apagar(luz_sala);
    """
    ejecutar_analisis(codigo_domotica)