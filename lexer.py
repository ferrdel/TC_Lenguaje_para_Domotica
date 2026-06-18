import re

class Token:
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}', L:{self.linea}, C:{self.columna})"

class Lexer:
    def __init__(self, codigo_fuente):
        self.codigo = codigo_fuente
        self.tokens = []
        self.errores = []
        
        # Biblioteca de palabras reservadas específicas del lenguaje de domótica
        self.palabras_reservadas = {
            'encender': 'ENCENDER',
            'apagar': 'APAGAR',
            'esperar': 'ESPERAR',
            'si': 'SI',
            'repetir': 'REPETIR'
        }
        
        # Biblioteca de expresiones regulares para cada tipo de token
        self.patrones = [
            ('PAREN_IZQ', re.compile(r'\(')),
            ('PAREN_DER', re.compile(r'\)')),
            ('LLAVE_IZQ', re.compile(r'\{')),
            ('LLAVE_DER', re.compile(r'\}')),
            ('PUNTO_COMA', re.compile(r';')),
            ('OPERADOR', re.compile(r'(==|<|>)')),
            ('NUMERO', re.compile(r'\d+')),
            ('IDENTIFICADOR', re.compile(r'[a-zA-Z_][a-zA-Z0-9_]*')),
        ]

    def tokenizar(self):
        lineas = self.codigo.splitlines()
        
        for num_linea, linea in enumerate(lineas, start=1):
            columna = 1
            while columna <= len(linea):
                caracter_actual = linea[columna - 1]
                
                # El lexer ignora espacios en blanco
                if caracter_actual.isspace():
                    columna += 1
                    continue
                
                match_detectado = False
                texto_restante = linea[columna - 1:]
                
                for tipo_token, regex in self.patrones:
                    match = regex.match(texto_restante)
                    if match:
                        valor = match.group(0)
                        
                        # Verificador de palabras reservadas
                        if tipo_token == 'IDENTIFICADOR' and valor in self.palabras_reservadas:
                            tipo_token = self.palabras_reservadas[valor]
                            
                        token = Token(tipo_token, valor, num_linea, columna)
                        self.tokens.append(token)
                        
                        columna += len(valor)
                        match_detectado = True
                        break
                #Acumulador de  errores léxicos
                if not match_detectado:
                    mensaje_error = f"Léxico: Símbolo no reconocido '{caracter_actual}' en L:{num_linea}, C:{columna}"
                    self.errores.append(mensaje_error)
                    columna += 1
                    
        return self.tokens