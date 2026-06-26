import streamlit as st
import graphviz
from lexer import Lexer
from parser_core import ParserDomotica
import io
import zipfile

# ========================================================
# [MÓDULO DE VISUALIZACIÓN] - RECORRIDO DEL AST (TREE WALK)
# ========================================================
def construir_grafo_recursivo(nodo, dot):
    if not nodo:
        return

    nodo_id = str(id(nodo))
    clase_nodo = nodo.__class__.__name__

    # Estilos por defecto (Modernos)
    forma = 'box'
    estilo = 'filled, rounded' # Bordes suaves
    color_fondo = '#F2F4F4'
    color_borde = '#BDC3C7'
    color_texto = '#2C3E50'
    etiqueta = "Desconocido"
    ramas = []

    if clase_nodo == "NodoPrograma":
        etiqueta = "Programa"
        color_fondo = '#2E86C1' # Combina con el botón principal
        color_borde = '#1B4F72'
        color_texto = 'white'
        ramas = nodo.comandos
    elif clase_nodo == "NodoComandoSimple":
        etiqueta = f"{nodo.accion}\n({nodo.parametro})"
        color_fondo = '#E8F8F5' # Verde agua muy suave
        color_borde = '#1ABC9C'
        ramas = []
    elif clase_nodo == "NodoCondicional":
        etiqueta = f"SI\n{nodo.variable} {nodo.operador} {nodo.valor_comparacion}"
        color_fondo = '#FEF9E7' # Amarillo pastel
        color_borde = '#F1C40F'
        ramas = nodo.bloque
    elif clase_nodo == "NodoRepeticion":
        etiqueta = f"REPETIR\n({nodo.iteraciones})"
        color_fondo = '#F5EEF8' # Púrpura muy suave
        color_borde = '#AF7AC5'
        ramas = nodo.bloque

    # Aplicamos el estilo al nodo
    dot.node(
        name=nodo_id, 
        label=etiqueta, 
        shape=forma, 
        style=estilo, 
        fillcolor=color_fondo, 
        color=color_borde,
        fontcolor=color_texto,
        penwidth='1.5' # Borde un poquito más grueso
    )

    for hijo in ramas:
        if hijo is not None:
            hijo_id = str(id(hijo))
            dot.edge(nodo_id, hijo_id)
            construir_grafo_recursivo(hijo, dot)


# ========================================================
# [PROCESAMIENTO BATCH] - MOTOR AISLADO PARA EXPORTACIONES
# ========================================================
def procesar_script_completo(codigo, nombre_archivo):
    """
    Encapsula el ciclo de vida completo del compilador (Lexer -> Parser -> AST).
    Se ejecuta en un contexto aislado para procesar archivos en segundo plano
    sin alterar el estado de la interfaz gráfica principal (Session State).
    """
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

    # [GENERACIÓN DE REPORTES]: Compilación de logs
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

    # [RENDERIZADO HEADLESS]: Armado del grafo en memoria sin inyección en UI
    grafo = None
    if parser and not parser.errores and hasattr(parser, 'arbol_ast') and parser.arbol_ast:
        grafo = graphviz.Digraph()
        
        # Atributos globales modernos para el grafo
        grafo.attr(
            rankdir='TB', 
            size='9,8', 
            bgcolor='transparent',
            splines='spline', # Líneas curvas y suaves
            nodesep='0.5',
            ranksep='0.8'
        )
        
        # Atributos globales para Nodos y Flechas
        grafo.attr('node', fontname='Segoe UI, Helvetica, sans-serif', fontsize='10', margin='0.2,0.1')
        grafo.attr('edge', color='#85929E', penwidth='1.2', arrowhead='vee', arrowsize='0.7')
        
        construir_grafo_recursivo(parser.arbol_ast, grafo)
    return reporte, grafo


# ========================================================
# [INTERFAZ REACTIVA] - CONTROLADOR PRINCIPAL (STREAMLIT)
# ========================================================
st.set_page_config(page_title="Compilador Domótica", layout="wide")
st.markdown("""
    <h1 style='text-align: center; background: -webkit-linear-gradient(#2E86C1, #85C1E9); 
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
    🏠 Analizador Sintáctico - Domótica
    </h1>
    <hr>
""", unsafe_allow_html=True)

# ========================================================
# [PERSONALIZACIÓN UI] - INYECCIÓN DE CSS
# ========================================================
st.markdown("""
<style>
    /* Estilo moderno para todos los botones */
    div.stButton > button:first-child {
        background-color: #2E86C1;
        color: white;
        border-radius: 8px;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    /* Efecto Hover (cuando pasas el mouse) */
    div.stButton > button:first-child:hover {
        background-color: #1B4F72;
        box-shadow: 0 6px 8px rgba(0,0,0,0.2);
        transform: translateY(-2px);
    }
    
    /* Suavizar los bordes de la consola y el grafo */
    div[data-testid="stContainer"] {
        border-radius: 12px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

col_izq, col_der = st.columns([1, 2], gap="large")

with col_izq:
    st.subheader("Carga de archivos")
    
    # Manejo explícito del estado de sesión para permitir resets limpios de la UI
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
        lista_nombres = list(nombres_archivos.keys())
        
        # [CONTROL DE ESTADO]: Inicialización del índice de navegación en memoria
        if "file_index" not in st.session_state:
            st.session_state.file_index = 0
            
        # Prevención de desbordamiento de índice ante la eliminación en caliente de archivos
        if st.session_state.file_index >= len(lista_nombres):
            st.session_state.file_index = 0
            
        # [NAVEGACIÓN RÁPIDA]: Controles de paginación bidireccional
        col_nav1, col_nav2 = st.columns(2)
        with col_nav1:
            if st.button("⬅️ Anterior", use_container_width=True, disabled=(st.session_state.file_index == 0)):
                st.session_state.file_index -= 1
                st.rerun()
        with col_nav2:
            if st.button("Siguiente ➡️", use_container_width=True, disabled=(st.session_state.file_index == len(lista_nombres) - 1)):
                st.session_state.file_index += 1
                st.rerun()
                
        # Sincronización del controlador selectbox con el estado de los botones
        archivo_seleccionado = st.selectbox(
            "📂 Script en análisis:", 
            options=lista_nombres, 
            index=st.session_state.file_index
        )
        
        if lista_nombres.index(archivo_seleccionado) != st.session_state.file_index:
            st.session_state.file_index = lista_nombres.index(archivo_seleccionado)
            st.rerun()
            
        archivo_actual = nombres_archivos[archivo_seleccionado]
    
    btn_limpiar = st.button("Limpiar Todo", width="stretch")

    if btn_limpiar:
        st.session_state.uploader_key += 1
        # Se reinicia el índice al limpiar la bandeja de entrada
        if "file_index" in st.session_state:
            st.session_state.file_index = 0
        st.rerun()

    st.markdown("---")
    
    st.subheader("Consola de errores")
    consola = st.container(height=400, border=True)
    
    reporte_actual_txt = ""
    grafo_actual = None

    if archivo_actual is not None:
        # [I/O DECODING]: Tolerancia a distintas codificaciones de texto (UTF-8 vs Latin-1)
        try:
            codigo = archivo_actual.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            codigo = archivo_actual.getvalue().decode("latin-1")
            
        reporte_actual_txt, grafo_actual = procesar_script_completo(codigo, archivo_actual.name)
        
        # [INSTANCIACIÓN REACTIVA]: Análisis en tiempo real para métricas de pantalla
        lexer_temp = Lexer(codigo)
        tokens_temp = lexer_temp.tokenizar()
        parser_temp = ParserDomotica(tokens_temp) if not lexer_temp.errores else None
        if parser_temp:
            try:
                parser_temp.parse_programa()
            except:
                pass
                
        total_errores = len(lexer_temp.errores) + (len(parser_temp.errores) if parser_temp else 0)

        # Dashboard de métricas lexicológicas
        col_m1, col_m2, col_m3 = consola.columns(3)
        col_m1.metric("Líneas", len(codigo.split('\n')))
        col_m2.metric("Tokens", len(tokens_temp))
        col_m3.metric("Errores", total_errores, delta=None if total_errores == 0 else "Revisar", delta_color="inverse")
        consola.markdown("---")

        # [PRESENTACIÓN DE DIAGNÓSTICO]: Filtrado y formateo de excepciones sintácticas
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
                    consola.markdown("### ❌ Errores Sintácticos en Archivo")
                    for err in errores_reales:
                        consola.error(err["mensaje"])
                if errores_colaterales:
                    consola.markdown("### ⚠️ Errores en Cascada (Colaterales)")
                    for err in errores_colaterales:
                        consola.warning(err["mensaje"])
            else:
                consola.success(f"✅ Análisis de '{archivo_actual.name}' completado sin errores.")
    else:
        consola.info("Esperando carga de archivos...")

    # ========================================================
    # [CONTROLADORES DE DESCARGA] - EXPORTACIÓN EN BYTES
    # ========================================================
    if archivos_subidos:
        st.markdown("<br>", unsafe_allow_html=True)
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button("📄 Bajar Reporte Actual", data=reporte_actual_txt, file_name=f"Reporte_{archivo_actual.name}.txt", use_container_width=True)
        with col_dl2:
            # Creación de buffer en memoria (RAM) para compresión ZIP sin tocar el disco duro
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
                st.graphviz_chart(grafo_actual, use_container_width=True)
            else:
                st.markdown("<br><br><br><br><center><i>Hay errores en el código. Arreglalos para generar el AST.</i></center>", unsafe_allow_html=True)
        else:
            st.markdown("<br><br><br><br><center><i>El árbol se generará aquí...</i></center>", unsafe_allow_html=True)

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