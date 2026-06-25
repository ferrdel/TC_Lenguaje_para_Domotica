import reglas_simples
import reglas_control
from ast_nodes import NodoPrograma

class ErrorSincronizacion(Exception):
    """Excepción silenciosa para abortar una regla rota sin crashear el parser."""
    pass

class ParserDomotica:
    def __init__(self, lista_tokens):
        self.tokens = lista_tokens
        self.posicion = 0
        self.token_actual = self.tokens[self.posicion] if self.tokens else None
        self.errores = [] 
        self.arbol_ast = None # Acá guardamos el árbol para Streamlit

    def avanzar(self):
        self.posicion += 1
        if self.posicion < len(self.tokens):
            self.token_actual = self.tokens[self.posicion]
        else:
            self.token_actual = None

    def sincronizar(self):
        tokens_seguros = ["PUNTO_COMA", "LLAVE_DER", "LLAVE_IZQ"]
        while self.token_actual and self.token_actual.tipo not in tokens_seguros:
            self.avanzar()
            
        if self.token_actual and self.token_actual.tipo == "PUNTO_COMA":
            self.avanzar()

    def consumir(self, tipo_esperado):
        if self.token_actual and self.token_actual.tipo == tipo_esperado:
            self.avanzar()
        else:
            encontrado = self.token_actual.tipo if self.token_actual else "FIN_DE_ARCHIVO"
            linea = self.token_actual.linea if self.token_actual else "desconocida"
            col = self.token_actual.columna if self.token_actual else "desconocida"
            
            self.errores.append({
                "tipo": "Real",
                "mensaje": f"Error Sintáctico [L:{linea}, C:{col}]: Se esperaba '{tipo_esperado}', pero se encontró '{encontrado}'"
            })
            raise ErrorSincronizacion()

    def parse_programa(self):
        lista_final_nodos = self.parse_lista_comandos()
        
        if self.token_actual is not None:
            self.errores.append({
                "tipo": "Consecuencia",
                "mensaje": f"Efecto Colateral [L:{self.token_actual.linea}]: Símbolo '{self.token_actual.valor}' huérfano al final del archivo"
            })
            
        # ¡Coronamos el árbol!
        self.arbol_ast = NodoPrograma(comandos=lista_final_nodos)
        return self.arbol_ast

    def parse_lista_comandos(self):
        lista_nodos = []
        first_comando = ["ENCENDER", "APAGAR", "ESPERAR", "SI", "REPETIR"]
        
        if not self.token_actual or self.token_actual.tipo == "LLAVE_DER":
            return lista_nodos
            
        if self.token_actual.tipo in first_comando:
            nodo = self.parse_comando()
            if nodo:
                lista_nodos.append(nodo)
            lista_nodos.extend(self.parse_lista_comandos())
        else:
            # CORRECCIÓN: Ahora es un error sintáctico REAL, no un efecto colateral
            self.errores.append({
                "tipo": "Real",
                "mensaje": f"Error Sintáctico [L:{self.token_actual.linea}]: Instrucción no válida '{self.token_actual.valor}'. Se esperaba un comando (encender, apagar, si, esperar, repetir)."
            })
            
            token_antes = self.token_actual
            self.sincronizar()
            if self.token_actual == token_antes:
                self.avanzar()
                
            lista_nodos.extend(self.parse_lista_comandos())
            
        return lista_nodos

    def parse_comando(self):
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
            self.sincronizar()
            
        return nodo