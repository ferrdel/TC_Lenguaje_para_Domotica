import reglas_simples
import reglas_control

class ParserDomotica:
    def __init__(self, lista_tokens):
        self.tokens = lista_tokens
        self.posicion = 0
        self.token_actual = self.tokens[self.posicion] if self.tokens else None
        self.errores = []  # Lista para acumular errores sintácticos

    def avanzar(self):
        """Mueve el puntero de análisis al siguiente token."""
        self.posicion += 1
        if self.posicion < len(self.tokens):
            self.token_actual = self.tokens[self.posicion]
        else:
            self.token_actual = None

    def sincronizar(self):
        """
        Recuperación de errores: Descarta tokens hasta encontrar un delimitador seguro
        para evitar una cascada de errores falsos.
        """
        tokens_seguros = ["PUNTO_COMA", "LLAVE_DER"]
        
        while self.token_actual and self.token_actual.tipo not in tokens_seguros:
            self.avanzar()
            
        # Si frenó en un token seguro, lo consumimos para limpiar la línea y seguir
        if self.token_actual and self.token_actual.tipo in tokens_seguros:
            self.avanzar()

    def consumir(self, tipo_esperado):
        """
        Verifica el token. Si hay error, lo anota en la lista y llama a sincronizar()
        en lugar de abortar el programa.
        """
        if self.token_actual and self.token_actual.tipo == tipo_esperado:
            self.avanzar()
        else:
            # 1. Registrar el error
            encontrado = self.token_actual.tipo if self.token_actual else "FIN_DE_ARCHIVO"
            linea = self.token_actual.linea if self.token_actual else "desconocida"
            col = self.token_actual.columna if self.token_actual else "desconocida"
            
            mensaje = f"Error Sintáctico [L:{linea}, C:{col}]: Se esperaba '{tipo_esperado}', pero se encontró '{encontrado}'"
            self.errores.append(mensaje)
            
            # 2. Intentar recuperar el contexto
            self.sincronizar()

    def parse_programa(self):
        """Regla inicial."""
        self.parse_lista_comandos()
        
        if self.token_actual is not None:
            self.errores.append(f"Error Sintáctico: Tokens huérfanos al final del archivo en L:{self.token_actual.linea}")
            
        # Reporte final
        if self.errores:
            print("\n[!] EL ANÁLISIS SINTÁCTICO FINALIZÓ CON ERRORES:")
            for err in self.errores:
                print(f" - {err}")
        else:
            print("\n[AST] Análisis sintáctico completado con éxito. Sin errores.")

    def parse_lista_comandos(self):
        """<lista_comandos> -> <comando> <lista_comandos> | ε"""
        first_comando = ["ENCENDER", "APAGAR", "ESPERAR", "SI", "REPETIR"]
        
        if self.token_actual and self.token_actual.tipo in first_comando:
            self.parse_comando()
            self.parse_lista_comandos()

    def parse_comando(self):
        """Distribuidor LL(1)"""
        if not self.token_actual:
            return
            
        tipo = self.token_actual.tipo
        
        if tipo == "ENCENDER":
            reglas_simples.parse_encender(self)
        elif tipo == "APAGAR":
            reglas_simples.parse_apagar(self)
        elif tipo == "ESPERAR":
            reglas_simples.parse_esperar(self)
        elif tipo == "SI":
            reglas_control.parse_condicional(self)
        elif tipo == "REPETIR":
            reglas_control.parse_repeticion(self)
        else:
            # Si el inicio del comando es cualquier otra cosa, anotamos y sincronizamos
            self.errores.append(f"Error Sintáctico [L:{self.token_actual.linea}]: Comando no reconocido '{tipo}'")
            self.sincronizar()