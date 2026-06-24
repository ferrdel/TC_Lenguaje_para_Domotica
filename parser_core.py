import reglas_simples
import reglas_control

class ErrorSincronizacion(Exception):
    """Excepción silenciosa para abortar una regla rota sin crashear el parser."""
    pass

class ParserDomotica:
    def __init__(self, lista_tokens):
        self.tokens = lista_tokens
        self.posicion = 0
        self.token_actual = self.tokens[self.posicion] if self.tokens else None
        self.errores = []  # Guardará diccionarios: {"tipo": "Real"|"Consecuencia", "mensaje": "..."}

    def avanzar(self):
        self.posicion += 1
        if self.posicion < len(self.tokens):
            self.token_actual = self.tokens[self.posicion]
        else:
            self.token_actual = None

    def sincronizar(self):
        """Descarta basura hasta encontrar un límite seguro de comando."""
        tokens_seguros = ["PUNTO_COMA", "LLAVE_DER", "LLAVE_IZQ"]
        
        while self.token_actual and self.token_actual.tipo not in tokens_seguros:
            self.avanzar()
            
        if self.token_actual and self.token_actual.tipo == "PUNTO_COMA":
            self.avanzar()

    def consumir(self, tipo_esperado):
        """Las fallas aquí son ERRORES REALES (rompen la estructura interna del comando)."""
        if self.token_actual and self.token_actual.tipo == tipo_esperado:
            self.avanzar()
        else:
            encontrado = self.token_actual.tipo if self.token_actual else "FIN_DE_ARCHIVO"
            linea = self.token_actual.linea if self.token_actual else "desconocida"
            col = self.token_actual.columna if self.token_actual else "desconocida"
            
            # Clasificado como ERROR REAL
            self.errores.append({
                "tipo": "Real",
                "mensaje": f"Error Sintáctico [L:{linea}, C:{col}]: Se esperaba '{tipo_esperado}', pero se encontró '{encontrado}'"
            })
            raise ErrorSincronizacion()

    def parse_programa(self):
        self.parse_lista_comandos()
        if self.token_actual is not None:
            # Ahora la basura del final se etiqueta correctamente como daño colateral
            self.errores.append({
                "tipo": "Consecuencia",
                "mensaje": f"Efecto Colateral [L:{self.token_actual.linea}]: Símbolo '{self.token_actual.valor}' huérfano al final del archivo"
            })

    def parse_lista_comandos(self):
        """Las fallas en el lazo principal son CONSECUENCIAS de un descarte previo (esquirlas de pánico)."""
        first_comando = ["ENCENDER", "APAGAR", "ESPERAR", "SI", "REPETIR"]
        
        if not self.token_actual or self.token_actual.tipo == "LLAVE_DER":
            return
            
        if self.token_actual.tipo in first_comando:
            self.parse_comando()
            self.parse_lista_comandos()
        else:
            # Clasificado como EFECTO COLATERAL (Consecuencia del modo pánico)
            self.errores.append({
                "tipo": "Consecuencia",
                "mensaje": f"Efecto Colateral [L:{self.token_actual.linea}]: Símbolo '{self.token_actual.valor}' huérfano debido a una sincronización previa"
            })
            
            token_antes = self.token_actual
            self.sincronizar()
            if self.token_actual == token_antes:
                self.avanzar()
                
            self.parse_lista_comandos()

    def parse_comando(self):
        if not self.token_actual:
            return
            
        tipo = self.token_actual.tipo
        
        try:
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
                self.errores.append({
                    "tipo": "Real",
                    "mensaje": f"Error Sintáctico [L:{self.token_actual.linea}]: Comando no reconocido '{tipo}'"
                })
                self.sincronizar()
                
        except ErrorSincronizacion:
            self.sincronizar()