import streamlit as st
import graphviz
from lexer import Lexer
from parser_core import ParserDomotica

# Configuración de página
st.set_page_config(page_title="Compilador Domótica", layout="wide")
st.title("🏠 Analizador Sintáctico - Domótica")

col_izq, col_der = st.columns([1, 2], gap="large")

with col_izq:
    st.subheader("Carga de Archivo")
    archivo_subido = st.file_uploader("Seleccioná tu script (.txt, .dom)", type=["txt", "dom"])
    
    btn_col1, btn_col2 = st.columns(2)
    with btn_col1:
        # Corregido el warning de depreciación
        btn_analizar = st.button("Analizar Sintaxis", type="primary", width="stretch")
    with btn_col2:
        btn_limpiar = st.button("Limpiar", width="stretch")

    if btn_limpiar:
        st.rerun()

    st.markdown("---")
    
    st.subheader("Consola de errores")
    # Ampliamos la altura de la consola para que sea más cómoda
    consola = st.container(height=450, border=True)
    
    # Banderas para saber si podemos graficar el AST real luego
    analisis_exitoso = False 

    if btn_analizar:
        if archivo_subido is None:
            consola.warning("⚠️ Por favor, cargá un archivo primero.")
        else:
            codigo = archivo_subido.getvalue().decode("utf-8")
            
            # --- 1. FASE LÉXICA REAL ---
            lexer = Lexer(codigo)
            tokens = lexer.tokenizar()
            
            hubo_errores = False
            
            if lexer.errores:
                hubo_errores = True
                consola.markdown("**[ERRORES LÉXICOS]**")
                for err in lexer.errores:
                    consola.error(err)
            
            # --- 2. FASE SINTÁCTICA REAL ---
            if not hubo_errores:
                parser = ParserDomotica(tokens)
                try:
                    parser.parse_programa()
                    
                    if parser.errores:
                        # Separamos y contamos para darle un feedback de calidad al usuario
                        errores_reales = [e for e in parser.errores if e["tipo"] == "Real"]
                        errores_colaterales = [e for e in parser.errores if e["tipo"] == "Consecuencia"]
                        
                        if errores_reales:
                            consola.markdown("### ❌ Errores Sintácticos Reales")
                            for err in errores_reales:
                                consola.error(err["mensaje"])
                        
                        if errores_colaterales:
                            consola.markdown("### ⚠️ Efectos Colaterales (Esquirlas de Sincronización)")
                            for err in errores_colaterales:
                                # Usamos warning (amarillo/naranja) para bajarle el tono visual
                                consola.warning(err["mensaje"])
                    else:
                        consola.success("✅ Análisis Léxico y Sintáctico completado sin errores.")
                        analisis_exitoso = True
                except Exception as e:
                    consola.error(f"Error Crítico: {str(e)}")
            else:
                consola.info("Proceso interrumpido por errores léxicos. Corríjalos para continuar al parser.")

with col_der:
    # --- PANEL DERECHO: AST ---
    st.subheader("AST (Árbol de Sintaxis Abstracta)")
    
    marco_grafo = st.container(height=600, border=True)
    
    with marco_grafo:
        if btn_analizar and archivo_subido is not None:
            # Gráfico de prueba para confirmar que funciona Graphviz
            arbol = graphviz.Digraph()
            arbol.attr(rankdir='TB', size='8,8')
            
            arbol.node('A', 'Programa')
            arbol.node('B', 'si (temp > 24)')
            arbol.node('C', 'encender(aire)')
            arbol.node('D', 'apagar(estufa)')
            
            arbol.edge('A', 'B')
            arbol.edge('B', 'C', label='Verdadero')
            arbol.edge('B', 'D', label='Falso')
            
            st.graphviz_chart(arbol, use_container_width=True)
        else:
            st.markdown("<br><br><br><br><center><i>El árbol se generará aquí...</i></center>", unsafe_allow_html=True)