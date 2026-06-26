# Analizador Léxico-Sintáctico para Domótica (TC2026)

Este proyecto implementa un compilador (Analizador Léxico, Analizador Sintáctico Descendente Predictivo y Generador de AST) desarrollado íntegramente en Python para un Lenguaje de Dominio Específico (DSL) enfocado en domótica.

## Requisitos Previos
Para ejecutar la interfaz gráfica y visualizar el Árbol de Sintaxis Abstracta (AST), es necesario tener instalado Python 3.8 o superior y las siguientes dependencias:

 Instalar la librería de interfaz web:
   pip install streamlit
 Instalar la librería de renderizado de grafos:
   pip install graphviz  
Además del paquete de Python, requiere tener el software Graphviz instalado en el sistema operativo y agregado al PATH, para las funcionalidades de descarga de grafos.


## Instruccion de Ejecucion
Abrir una terminal en el directorio raíz del proyecto
Ejecutar el siguiente comando para iniciar el servidor local:
    streamlit run app.py
Se abrirá automáticamente una pestaña en el navegador web.

## Guia de Pruebas
El repositorio incluye una batería de pruebas diseñada para evaluar la recursividad, el anidamiento profundo y la tolerancia a fallos. Esto se encuentra en el directorio /Pruebas y Resultados:

    /Casos de Prueba: Contiene los archivos de código fuente originales (.txt). Estos son los scripts que deben cargarse en la interfaz web.

    /Resultados Generados: Contiene los reportes de compilación (.txt) extraídos directamente de la plataforma. Funcionan como el registro de las salidas esperadas para cada caso.

¿Cómo ejecutar las pruebas?

    En la interfaz web, diríjase al panel lateral izquierdo "Control de Archivos".

    Seleccione o arrastre los archivos ubicados en la carpeta /Pruebas y Resultados/Casos de Prueba hacia la zona de carga.

    El motor procesará automáticamente los scripts, renderizando el diagrama AST en tiempo real para las cadenas válidas, o aislando e informando los errores sintácticos reales en la consola para los casos destructivos.

    Puede comparar el comportamiento obtenido en pantalla con los reportes oficiales ubicados en la carpeta /Resultados Generados.


