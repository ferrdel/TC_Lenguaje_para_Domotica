import re

# ==========================================
# ESTRUCTURA DE COMPONENTE LÉXICO (TOKEN)
# ==========================================
class Token:
    """
    Representa la unidad atómica de información extraída del código fuente.
    Almacena la categoría gramatical (tipo), el lexema exacto (valor) y 
    su trazabilidad espacial (línea y columna) para el reporte de errores.
    """
    def __init__(self, tipo, valor, linea, columna):
        self.tipo = tipo
        self.valor = valor
        self.linea = linea
        self.columna = columna

    def __repr__(self):
        return f"Token({self.tipo}, '{self.valor}', L:{self.linea}, C:{self.columna})"

# ==========================================
# MOTOR DEL ANALIZADOR LÉXICO (SCANNER)
# ==========================================
class Lexer:
    """
    Implementación de un escáner basado en Autómatas Finitos Deterministas (DFA).
    Lee el flujo de caracteres, ignora espacios (blanks) y agrupa caracteres en tokens válidos.
    """
    def __init__(self, codigo_fuente):
        self.codigo = codigo_fuente
        self.tokens = []
        self.errores = []
        
        # [TABLA DE PALABRAS RESERVADAS] (Keywords)
        # Diccionario para diferenciarlas de los identificadores comunes en tiempo de ejecución (O(1)).
        self.palabras_reservadas = {
            'encender': 'ENCENDER',
            'apagar': 'APAGAR',
            'esperar': 'ESPERAR',
            'si': 'SI',
            'repetir': 'REPETIR'
        }
        
        # [CONJUNTO DE EXPRESIONES REGULARES] (Regex Patterns)
        # El orden es crítico: determina la precedencia del "Match Más Largo" (Maximal Munch).
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
        """
        Función central de escaneo. Recorre el buffer de entrada línea por línea y
        aplica las expresiones regulares para extraer los tokens válidos.
        """
        lineas = self.codigo.splitlines()
        
        for num_linea, linea in enumerate(lineas, start=1):
            columna = 1
            while columna <= len(linea):
                caracter_actual = linea[columna - 1]
                
                # [FILTRO DE BLANCOS]: El compilador descarta tabulaciones, espacios y saltos de línea.
                if caracter_actual.isspace():
                    columna += 1
                    continue
                
                match_detectado = False
                texto_restante = linea[columna - 1:]
                
                # [EVALUACIÓN DE DFA]: Itera sobre la tabla de patrones buscando coincidencias.
                for tipo_token, regex in self.patrones:
                    match = regex.match(texto_restante)
                    if match:
                        valor = match.group(0)
                        
                        # [RESOLUCIÓN DE AMBIGÜEDAD]: Verifica si el identificador extraído 
                        # pertenece en realidad al conjunto cerrado de palabras reservadas.
                        if tipo_token == 'IDENTIFICADOR' and valor in self.palabras_reservadas:
                            tipo_token = self.palabras_reservadas[valor]
                            
                        # [EMISIÓN]: Instancia y almacena el componente léxico.
                        token = Token(tipo_token, valor, num_linea, columna)
                        self.tokens.append(token)
                        
                        # Desplazamiento del puntero de lectura (buffer pointer).
                        columna += len(valor)
                        match_detectado = True
                        break
                
                # [MANEJO DE ERRORES LÉXICOS EN MODO PÁNICO LOCAL]
                # Si ningún autómata reconoce el prefijo actual, se reporta la falla
                # y se avanza forzosamente un caracter para no bloquear la lectura del resto del archivo.
                if not match_detectado:
                    mensaje_error = f"Léxico: Símbolo no reconocido '{caracter_actual}' en L:{num_linea}, C:{columna}"
                    self.errores.append(mensaje_error)
                    columna += 1
                    
        return self.tokens