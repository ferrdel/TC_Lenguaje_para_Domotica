import streamlit as st
import graphviz
from lexer import Lexer
from parser_core import ParserDomotica
import io
import zipfile

# ========================================================
# FUNCIÓN RECURSIVA DEL AST
# ========================================================
def construir_grafo_recursivo(nodo, dot):
    if not nodo:
        return

    nodo_id = str(id(nodo))
    clase_nodo = nodo.__class__.__name__

    forma = 'ellipse'
    color_fondo = '#EAEDED'
    etiqueta = "Desconocido"
    ramas = []

    if clase_nodo == "NodoPrograma":
        etiqueta = "Programa"
        color_fondo = '#AED6F1'
        ramas = nodo.comandos
    elif clase_nodo == "NodoComandoSimple":
        etiqueta = f"{nodo.accion}({nodo.parametro});"
        forma = 'box'
        color_fondo = '#D4EFDF'
    elif clase_nodo == "NodoCondicional":
        etiqueta = f"SI ({nodo.variable} {nodo.operador} {nodo.valor_comparacion})"
        forma = 'diamond'
        color_fondo = '#FCF3CF'
        ramas = nodo.bloque
    elif clase_nodo == "NodoRepeticion":
        etiqueta = f"REPETIR ({nodo.iteraciones})"
        forma = 'hexagon'
        color_fondo = '#EBDEF0'
        ramas = nodo.bloque

    dot.node(name=nodo_id, label=etiqueta, shape=forma, style='filled', fillcolor=color_fondo)

    for hijo in ramas:
        if hijo is not None:
            hijo_id = str(id(hijo))
            dot.edge(nodo_id, hijo_id)
            construir_grafo_recursivo(hijo, dot)


# ========================================================
# MOTOR DE PROCESAMIENTO EN SEGUNDO PLANO (Para exportaciones)
# ========================================================
def procesar_script_completo(codigo, nombre_archivo):
    """Procesa un script y devuelve el texto del reporte y el objeto Graphviz si es válido."""
    lexer = Lexer(codigo)
    tokens = lexer.tokenizar()
    
    parser = None
    hubo_errores_lexicos = len(lexer.errores) > 0
    
    if not hubo_errores_lexicos:
        parser = ParserDomotica(tokens)
        try:
            parser.parse_programa()
        except Exception:
            pass

    # 1. Armar el reporte de texto
    reporte = f"=== REPORTE DE ANÁLISIS SINTÁCTICO: {nombre_archivo} ===\n\n"
    reporte += f"[CÓDIGO ORIGINAL]\n{codigo}\n\n[RESULTADOS]\n"
    
    if hubo_errores_lexicos:
        reporte += "ESTADO: ❌ Rechazado (Errores Léxicos)\n"
        for err in lexer.errores:
            reporte += f"- {err}\n"
    elif parser and parser.errores:
        reporte += "ESTADO: ❌ Rechazado (Errores Sintácticos)\n"
        for err in parser.errores:
            reporte += f"- {err['mensaje']}\n"
    else:
        reporte += "ESTADO: ✅ Aprobado (AST Generado correctamente)\n"

    # 2. Armar el Grafo (solo si no hay errores)
    grafo = None
    if parser and not parser.errores and hasattr(parser, 'arbol_ast') and parser.arbol_ast:
        grafo = graphviz.Digraph()
        grafo.attr(rankdir='TB', size='9,8')
        grafo.attr('node', fontname='Helvetica', fontsize='11')
        grafo.attr('edge', color='gray', arrowhead='vee', arrowsize='1')
        construir_grafo_recursivo(parser.arbol_ast, grafo)

    return reporte, grafo


# ========================================================
# INTERFAZ WEB PRINCIPAL
# ========================================================
st.set_page_config(page_title="Compilador Domótica", layout="wide")
st.title("🏠 Analizador Sintáctico - Domótica")

col_izq, col_der = st.columns([1, 2], gap="large")

with col_izq:
    st.subheader("Control de Archivos")
    
    if "uploader_key" not in st.session_state:
        st.session_state.uploader_key = 0
    
    with st.expander("📥 Cargar nuevos scripts", expanded=True):
        archivos_subidos = st.file_uploader(
            "Arrastrá tus casos de prueba acá", 
            type=["txt", "dom"], 
            accept_multiple_files=True,
            key=str(st.session_state.uploader_key)
        )
    
    archivo_actual = None
    nombres_archivos = {}
    if archivos_subidos:
        nombres_archivos = {archivo.name: archivo for archivo in archivos_subidos}
        archivo_seleccionado = st.selectbox("📂 Script en análisis:", options=list(nombres_archivos.keys()))
        archivo_actual = nombres_archivos[archivo_seleccionado]
    
    btn_limpiar = st.button("Limpiar Todo", width="stretch")

    if btn_limpiar:
        st.session_state.uploader_key += 1
        st.rerun()

    st.markdown("---")
    
    st.subheader("Consola de errores")
    consola = st.container(height=400, border=True)
    
    # Variables globales para el renderizado
    reporte_actual_txt = ""
    grafo_actual = None

    if archivo_actual is not None:
        try:
            codigo = archivo_actual.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            codigo = archivo_actual.getvalue().decode("latin-1")
            
        # Ejecutamos el motor centralizado
        reporte_actual_txt, grafo_actual = procesar_script_completo(codigo, archivo_actual.name)
        
        # Leemos los datos en crudo para las tarjetas visuales
        lexer_temp = Lexer(codigo)
        tokens_temp = lexer_temp.tokenizar()
        parser_temp = ParserDomotica(tokens_temp) if not lexer_temp.errores else None
        if parser_temp:
            try:
                parser_temp.parse_programa()
            except:
                pass
                
        total_errores = len(lexer_temp.errores) + (len(parser_temp.errores) if parser_temp else 0)

        col_m1, col_m2, col_m3 = consola.columns(3)
        col_m1.metric("Líneas", len(codigo.split('\n')))
        col_m2.metric("Tokens", len(tokens_temp))
        col_m3.metric("Errores", total_errores, delta=None if total_errores == 0 else "Revisar", delta_color="inverse")
        consola.markdown("---")

        if lexer_temp.errores:
            consola.markdown("**[ERRORES LÉXICOS]**")
            for err in lexer_temp.errores:
                consola.error(err)
            consola.info("Proceso interrumpido por errores léxicos.")
        elif parser_temp:
            if parser_temp.errores:
                errores_reales = [e for e in parser_temp.errores if e["tipo"] == "Real"]
                errores_colaterales = [e for e in parser_temp.errores if e["tipo"] == "Consecuencia"]
                if errores_reales:
                    consola.markdown("### ❌ Errores Sintácticos Reales")
                    for err in errores_reales:
                        consola.error(err["mensaje"])
                if errores_colaterales:
                    consola.markdown("### ⚠️ Efectos Colaterales (Esquirlas)")
                    for err in errores_colaterales:
                        consola.warning(err["mensaje"])
            else:
                consola.success(f"✅ Análisis de '{archivo_actual.name}' completado sin errores.")
    else:
        consola.info("Esperando carga de archivos...")

    # --- BOTONES DE DESCARGA DE REPORTES (IZQUIERDA) ---
    if archivos_subidos:
        st.markdown("<br>", unsafe_allow_html=True)
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("📄 Bajar Reporte Actual", data=reporte_actual_txt, file_name=f"Reporte_{archivo_actual.name}.txt", use_container_width=True)
        with col_dl2:
            zip_buffer_txt = io.BytesIO()
            with zipfile.ZipFile(zip_buffer_txt, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for nombre, arch in nombres_archivos.items():
                    cod = arch.getvalue().decode("utf-8", errors="replace")
                    rep_txt, _ = procesar_script_completo(cod, nombre)
                    zip_file.writestr(f"Reporte_{nombre}.txt", rep_txt)
            st.download_button("📚 Bajar Todos (ZIP)", data=zip_buffer_txt.getvalue(), file_name="Reportes_Domotica.zip", mime="application/zip", use_container_width=True)


with col_der:
    titulo_ast = f"AST - {archivo_actual.name}" if archivo_actual else "AST (Árbol de Sintaxis Abstracta)"
    st.subheader(titulo_ast)
    
    marco_grafo = st.container(border=True)
    
    with marco_grafo:
        if archivo_actual is not None:
            if grafo_actual:
                # El componente de Streamlit tiene un botón de "Pantalla completa" en la esquina superior derecha
                st.graphviz_chart(grafo_actual, use_container_width=True)
            else:
                st.markdown("<br><br><br><br><center><i>Hay errores en el código. Arreglalos para generar el AST.</i></center>", unsafe_allow_html=True)
        else:
            st.markdown("<br><br><br><br><center><i>El árbol se generará aquí...</i></center>", unsafe_allow_html=True)

    # --- BOTONES DE DESCARGA DE IMÁGENES (DERECHA) ---
    if archivos_subidos:
        st.markdown("<br>", unsafe_allow_html=True)
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            if grafo_actual:
                png_bytes = grafo_actual.pipe(format='png')
                st.download_button("🖼️ Descargar AST Actual (.png)", data=png_bytes, file_name=f"AST_{archivo_actual.name}.png", mime="image/png", use_container_width=True)
            else:
                st.button("🖼️ Descargar AST Actual (.png)", disabled=True, use_container_width=True, help="Corregí los errores para habilitar la descarga")
        with col_img2:
            zip_buffer_img = io.BytesIO()
            with zipfile.ZipFile(zip_buffer_img, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for nombre, arch in nombres_archivos.items():
                    cod = arch.getvalue().decode("utf-8", errors="replace")
                    _, g = procesar_script_completo(cod, nombre)
                    if g:
                        zip_file.writestr(f"AST_{nombre.replace('.txt', '').replace('.dom', '')}.png", g.pipe(format='png'))
            st.download_button("📦 Descargar Todos los AST (.zip)", data=zip_buffer_img.getvalue(), file_name="Arboles_Domotica.zip", mime="application/zip", use_container_width=True)