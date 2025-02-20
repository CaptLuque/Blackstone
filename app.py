import streamlit as st
import requests
import tempfile
import os
from datetime import datetime
import pandas as pd
import time
import re
from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
from typing import List, Dict, Optional
import base64
from io import BytesIO

# API Key fija
GEMINI_API_KEY = "AIzaSyBa5Rp_1wlQ73FNCbotBoPXxzZImz5q5Hg"

def initialize_agents() -> tuple[Agent, Agent, Agent]:
    try:
        model = Gemini(id="gemini-2.0-flash-exp", api_key=GEMINI_API_KEY)
        
        content_agent = Agent(
            model=model,
            instructions=[
                "Eres un experto en análisis de contenido de Instagram que:",
                "1. Identifica patrones en el tipo de contenido que genera más engagement",
                "2. Analiza el tono y estilo de comunicación en las publicaciones",
                "3. Evalúa la efectividad de los copys y llamadas a la acción",
                "4. Detecta tendencias en el contenido más exitoso",
                "Se específico y proporciona recomendaciones accionables"
            ],
            markdown=True
        )

        engagement_agent = Agent(
            model=model,
            instructions=[
                "Eres un experto en análisis de engagement que:",
                "1. Analiza patrones de interacción y engagement",
                "2. Identifica qué tipo de posts generan más interacción",
                "3. Sugiere estrategias para aumentar el engagement",
                "4. Evalúa la calidad de las interacciones",
                "Enfoque en métricas y mejoras prácticas"
            ],
            markdown=True
        )

        strategy_agent = Agent(
            model=model,
            tools=[DuckDuckGoTools()],
            instructions=[
                "Eres un experto en estrategia de contenido que:",
                "1. Identifica oportunidades de mejora en la estrategia",
                "2. Analiza la competencia y tendencias del sector",
                "3. Sugiere ideas de contenido y temas a tratar",
                "4. Proporciona un plan de acción concreto",
                "Enfoque en recomendaciones estratégicas y planificación"
            ],
            markdown=True
        )
        
        return content_agent, engagement_agent, strategy_agent
    except Exception as e:
        st.error(f"Error initializing agents: {str(e)}")
        return None, None, None

def analyze_instagram_posts(posts_data: List[Dict], progress_callback=None) -> Dict:
    """
    Analiza los posts de Instagram usando los agentes de IA.
    
    Args:
        posts_data: Lista de diccionarios con información de cada post
        progress_callback: Función opcional para actualizar el progreso
    
    Returns:
        Dict con los resultados del análisis de cada agente
    """
    content_agent, engagement_agent, strategy_agent = initialize_agents()
    
    if not all([content_agent, engagement_agent, strategy_agent]):
        raise Exception("Error al inicializar los agentes")

    try:
        results = {}
        
        # Análisis de Contenido
        if progress_callback:
            progress_callback("🎨 Analizando contenido...")
        
        content_prompt = f"""
        Analiza los siguientes posts de Instagram:
        {posts_data}
        
        Proporciona insights sobre:
        1. Patrones en el contenido más exitoso
        2. Tono y estilo de comunicación
        3. Efectividad de los copys
        4. Recomendaciones de mejora
        
        Por favor, formatea tu respuesta con encabezados claros y puntos de viñeta.
        """
        content_response = content_agent.run(message=content_prompt)
        results['content_analysis'] = content_response.content
        
        # Análisis de Engagement
        if progress_callback:
            progress_callback("💫 Analizando engagement...")
            
        engagement_prompt = f"""
        Analiza las métricas de engagement de estos posts:
        {posts_data}
        
        Proporciona insights sobre:
        1. Patrones de engagement
        2. Mejores horarios y días
        3. Tipos de contenido más efectivos
        4. Estrategias para aumentar la interacción
        
        Por favor, formatea tu respuesta con encabezados claros y puntos de viñeta.
        """
        engagement_response = engagement_agent.run(message=engagement_prompt)
        results['engagement_analysis'] = engagement_response.content
        
        # Análisis Estratégico
        if progress_callback:
            progress_callback("🎯 Desarrollando estrategia...")
            
        strategy_prompt = f"""
        Basado en el análisis de estos posts:
        {posts_data}
        
        Proporciona:
        1. Recomendaciones estratégicas
        2. Ideas de contenido futuro
        3. Oportunidades de mejora
        4. Plan de acción concreto
        
        Por favor, formatea tu respuesta con encabezados claros y puntos de viñeta.
        """
        strategy_response = strategy_agent.run(message=strategy_prompt)
        results['strategy_analysis'] = strategy_response.content
        
        return results
        
    except Exception as e:
        raise Exception(f"Error en el análisis: {str(e)}")

def configurar_pagina():
    st.set_page_config(
        page_title="Blackstone",
        page_icon="🎨",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Estilo global para tema claro
    st.markdown("""
        <style>
        .main {
            background-color: white;
        }
        
        h1, h2, h3, h4, h5, h6 {
            color: #333;
        }
        
        p {
            color: #666;
        }
        
        .stMetric {
            background-color: white;
            border: 1px solid #ddd;
            border-radius: 5px;
            padding: 1rem;
        }
        
        .stMetric:hover {
            border-color: #ccc;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        /* Estilo para el valor de la métrica */
        .stMetric [data-testid="stMetricValue"] {
            color: #1f77b4 !important;
            font-size: 24px !important;
            font-weight: bold !important;
        }
        
        /* Estilo para la etiqueta de la métrica */
        .stMetric [data-testid="stMetricLabel"] {
            color: #666 !important;
            font-size: 14px !important;
        }
        </style>
    """, unsafe_allow_html=True)

def menu_lateral():
    with st.sidebar:
        # Estilo personalizado para el menú lateral
        st.markdown("""
            <style>
            [data-testid="stSidebar"][aria-expanded="true"]{
                min-width: 250px;
                max-width: 250px;
                background-color: white;
            }
            
            [data-testid="stSidebar"] [data-testid="stMarkdown"] {
                padding: 0;
            }
            
            .sidebar-header {
                padding: 1rem;
                margin-bottom: 2rem;
                text-align: center;
            }
            
            .sidebar-subtitle {
                color: #666;
                font-size: 14px;
                margin: 0.5rem 0 1.5rem 0;
                text-align: center;
            }
            
            .stButton>button {
                background-color: white;
                color: #333;
                border: 1px solid #ddd;
                padding: 0.5rem 1rem;
                font-size: 16px;
                width: 100%;
                margin: 0.25rem 0;
                display: flex;
                align-items: center;
                transition: all 0.2s;
            }
            
            .stButton>button:hover {
                background-color: #f8f9fa;
                border-color: #ccc;
            }
            
            .stButton>button[data-testid="baseButton-secondary"] {
                background-color: white;
            }
            
            .stButton>button[data-testid="baseButton-primary"] {
                background-color: #f0f2f6;
                font-weight: bold;
            }
            </style>
        """, unsafe_allow_html=True)
        
        # Obtener la ruta del directorio actual
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "assets", "blackstone_logo.png")
        
        try:
            # Logo usando el componente nativo de Streamlit
            st.image(logo_path, width=200)
        except:
            # Si no encuentra la imagen, mostrar el título como texto
            st.title("Blackstone")
            
        st.markdown('<p class="sidebar-subtitle">Agencia creativa</p>', unsafe_allow_html=True)
        
        # Inicializar la opción si no existe
        if 'menu_option' not in st.session_state:
            st.session_state.menu_option = "Inicio"
        
        # Opciones del menú con iconos
        opciones = {
            "Inicio": "🏠",
            "Subir Documento": "📄",
            "Enviar mail accesos": "📧",
            "Análisis Instagram": "📊",
            "Crear Cliente": "👥",
            "Crear Análisis": "📈",
            "Design Agent": "🎨",
            "Cliente Conversacional": "💬",
            "Otra Función": "⚙️"
        }
        
        # Crear los botones del menú
        for texto, icono in opciones.items():
            if st.button(
                f"{icono}  {texto}",
                key=f"btn_{texto}",
                use_container_width=True,
                type="secondary" if st.session_state.menu_option != texto else "primary"
            ):
                st.session_state.menu_option = texto
                st.rerun()
        
    return st.session_state.menu_option

def pagina_inicio():
    st.title("Bienvenido a MARTA PRO para Blackstone")
    st.write("Selecciona una opción del menú lateral para comenzar.")

def subir_documento():
    st.title("Subir Documento y Activar Webhook")
    
    archivo_subido = st.file_uploader("Selecciona un documento", type=['pdf', 'doc', 'docx', 'txt'])
    webhook_url = "HTTPS://marta-pro-n8n.onrender.com:443/webhook/2fea388c-97bf-486c-91af-05b83c13a0d8"
    
    if archivo_subido is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(archivo_subido.name)[1]) as tmp_file:
            tmp_file.write(archivo_subido.getvalue())
            documento_url = os.path.abspath(tmp_file.name)
        
        st.success(f"Documento subido: {archivo_subido.name}")
        
        if st.button("Activar Webhook"):
            try:
                payload = {
                    "documento_url": documento_url,
                    "nombre_archivo": archivo_subido.name
                }
                
                response = requests.post(webhook_url, json=payload)
                
                if response.status_code == 200:
                    st.success("Webhook activado exitosamente!")
                else:
                    st.error(f"Error al activar el webhook: {response.status_code}")
                    
            except Exception as e:
                st.error(f"Error: {str(e)}")
            
            os.unlink(tmp_file.name)

def enviar_mail_accesos():
    st.title("Solicitud de Accesos")
    
    email = st.text_input(
        "Correo electrónico",
        placeholder="ejemplo@empresa.com",
        key="email_input"
    )

    email_valido = True
    if email:
        if not '@' in email or not '.' in email:
            st.warning("Por favor, introduce un email válido")
            email_valido = False
    
    st.write("Selecciona los accesos que necesitas:")

    col1, col2 = st.columns(2)
    
    with col1:
        acceso_meta = st.checkbox("Acceso a Meta")
        acceso_instagram = st.checkbox("Acceso a Instagram")
    
    with col2:
        acceso_logo = st.checkbox("Logo")
        acceso_identidad = st.checkbox("Identidad visual")

    if st.button("Enviar Solicitud"):
        if not email:
            st.error("Por favor, introduce un email")
            return
        
        if not email_valido:
            st.error("Por favor, introduce un email válido")
            return
            
        webhook_url = "HTTPS://marta-pro-n8n.onrender.com:443/webhook/2fea388c-97bf-486c-91af-05b83c13a0d8"
        
        try:
            payload = {
                "email": email,
                "accesos_solicitados": {
                    "meta": acceso_meta,
                    "instagram": acceso_instagram,
                    "logo": acceso_logo,
                    "identidad_visual": acceso_identidad
                },
                "fecha_solicitud": str(datetime.now())
            }
            
            response = requests.post(webhook_url, json=payload)
            
            if response.status_code == 200:
                st.success("¡Solicitud enviada exitosamente!")
                st.write("Resumen de la solicitud:")
                st.write(f"📧 Email: {email}")
                st.write("Accesos solicitados:")
                for acceso, valor in payload["accesos_solicitados"].items():
                    if valor:
                        st.write(f"✓ {acceso.replace('_', ' ').title()}")
            else:
                st.error(f"Error al enviar la solicitud: {response.status_code}")
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

def analisis_instagram():
    st.title("Análisis de Usuario de Instagram")
    st.write("Introduce el nombre de usuario de Instagram para generar un informe")
    
    usuario_instagram = st.text_input(
        "Usuario de Instagram",
        placeholder="@usuario",
        key="instagram_input"
    )
    
    if st.button("Generar Informe"):
        if not usuario_instagram:
            st.error("Por favor, introduce un nombre de usuario")
            return
            
        # Eliminar el @ si el usuario lo incluyó
        usuario_instagram = usuario_instagram.strip('@')
        
        # Inicializar variables en session_state si no existen
        if 'instagram_data' not in st.session_state:
            st.session_state.instagram_data = None
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = None
        
        webhook_url = "HTTPS://marta-pro-n8n.onrender.com:443/webhook/2fea388c-97bf-486c-91af-05b83c13a0d8"
        
        try:
            params = {
                "usuario_instagram": usuario_instagram,
                "fecha_solicitud": str(datetime.now()),
                "tipo_informe": "analisis_perfil"
            }
            
            # Aumentar el timeout y mostrar progreso
            progress_text = "Generando informe... Esto puede tardar hasta 5 minutos"
            progress_bar = st.progress(0)
            
            with st.spinner(progress_text):
                try:
                    # Hacer la petición con un timeout más largo
                    response = requests.get(webhook_url, params=params, timeout=300)  # 5 minutos
                    
                    progress_bar.progress(25)
                    st.write("Respuesta recibida del servidor...")
                    
                    if response.status_code == 200:
                        datos = response.json()
                        progress_bar.progress(50)
                        st.write("Procesando datos...")
                        
                        if datos and isinstance(datos, list):
                            # Guardar datos en session_state
                            st.session_state.instagram_data = datos
                            # No llamar a display_instagram_analysis aquí
                            progress_bar.progress(100)
                            st.success("¡Informe generado exitosamente!")
                            st.rerun()  # Forzar recarga para mostrar los datos
                        else:
                            st.error("Los datos recibidos no tienen el formato esperado")
                    else:
                        st.error(f"Error al solicitar el informe: {response.status_code}")
                        st.write("Respuesta del servidor:", response.text)
                
                except requests.Timeout:
                    st.error("La solicitud ha excedido el tiempo de espera (5 minutos). Por favor, inténtalo de nuevo.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                finally:
                    progress_bar.empty()
                
        except Exception as e:
            st.error(f"Error: {str(e)}")

    # Mostrar los datos solo una vez, fuera del botón
    if hasattr(st.session_state, 'instagram_data') and st.session_state.instagram_data is not None:
        df = pd.DataFrame(st.session_state.instagram_data)
        display_instagram_analysis(df, usuario_instagram)

def display_instagram_analysis(df, usuario_instagram):
    """Función separada para mostrar el análisis de Instagram"""
    # Mostrar estadísticas básicas con formato de números
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric("Total Posts", f"{len(df):,}")
    with col2:
        if ' Cantidad de Likes' in df.columns:
            st.metric("Total Likes", f"{int(df[' Cantidad de Likes'].sum()):,}")
    with col3:
        if ' Cantidad de Comentarios' in df.columns:
            st.metric("Total Comentarios", f"{int(df[' Cantidad de Comentarios'].sum()):,}")
    with col4:
        if ' Cantidad de Likes' in df.columns:
            media_likes = df[' Cantidad de Likes'].mean()
            st.metric("Media de Likes", f"{int(media_likes):,}")
    with col5:
        if ' Cantidad de Comentarios' in df.columns:
            media_comentarios = df[' Cantidad de Comentarios'].mean()
            st.metric("Media de Comentarios", f"{int(media_comentarios):,}")

    # Mostrar los posts en forma de lista detallada
    st.subheader("Detalle de publicaciones")

    # Estilo CSS para las filas
    st.markdown("""
        <style>
        .post-container {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            background-color: white;
        }
        .post-info {
            margin-left: 15px;
        }
        .post-stats {
            display: flex;
            gap: 15px;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Mostrar cada post
    for index, post in df.iterrows():
        st.markdown("---")
        cols = st.columns([1, 2])  # Proporción 1:2 para imagen y datos
        
        # Columna de imagen
        with cols[0]:
            if ' Imagen URL' in df.columns:
                try:
                    # Extraer la URL de la imagen del formato IMAGE("url")
                    url_match = re.search(r'IMAGE\("([^"]+)"', str(post[' Imagen URL']))
                    if url_match:
                        url = url_match.group(1)
                        # Asegurar que usamos HTTPS
                        if url.startswith('http:'):
                            url = url.replace('http:', 'https:')
                        
                        # Usar el componente nativo de Streamlit para imágenes
                        st.image(
                            url,
                            use_container_width=True,
                            output_format="auto",
                            caption=f"Post de {post[' Username']}" if ' Username' in df.columns else None
                        )
                    else:
                        st.warning("URL de imagen no válida")
                except Exception as e:
                    st.warning(f"Error al cargar la imagen: {str(e)}")
        
        # Columna de información
        with cols[1]:
            # Información básica
            if 'Usuario' in df.columns:
                st.markdown(f"**Usuario:** {post['Usuario']}")
            if ' Username' in df.columns:
                st.markdown(f"**Username:** {post[' Username']}")
            
            # Estadísticas en una fila
            stats_cols = st.columns(3)
            with stats_cols[0]:
                if ' Cantidad de Likes' in df.columns:
                    st.markdown(f"👍 **Likes:** {post[' Cantidad de Likes']}")
            with stats_cols[1]:
                if ' Cantidad de Comentarios' in df.columns:
                    st.markdown(f"💬 **Comentarios:** {post[' Cantidad de Comentarios']}")
            with stats_cols[2]:
                if ' Fecha de Publicación' in df.columns:
                    fecha = pd.to_datetime(post[' Fecha de Publicación']).strftime('%Y-%m-%d')
                    st.markdown(f"📅 **Fecha:** {fecha}")
            
            # Primer Comentario
            if ' Primer Comentario' in df.columns and isinstance(post[' Primer Comentario'], str):
                with st.expander("Ver primer comentario"):
                    st.markdown(post[' Primer Comentario'])
            
            # Hashtags y menciones
            if ' Hashtags' in df.columns and isinstance(post[' Hashtags'], str):
                with st.expander("Ver hashtags"):
                    st.markdown(post[' Hashtags'])
            
            if ' Menciones' in df.columns and isinstance(post[' Menciones'], str):
                with st.expander("Ver menciones"):
                    st.markdown(post[' Menciones'])
            
            # URL del post
            if ' URL del Post' in df.columns and isinstance(post[' URL del Post'], str):
                st.markdown(f"🔗 [Ver en Instagram]({post[' URL del Post']})")
            
            # Información adicional
            if ' Es Publicidad' in df.columns:
                es_publicidad = post[' Es Publicidad']
                if pd.api.types.is_bool_dtype(type(es_publicidad)):
                    st.markdown(f"🎯 **Publicidad:** {'Sí' if es_publicidad else 'No'}")

    # Sección de acciones
    st.markdown("---")
    st.subheader("📊 Acciones Disponibles")
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.download_button(
            label="📥 Descargar datos como CSV",
            data=df.to_csv(index=False),
            file_name=f'instagram_analysis_{usuario_instagram}.csv',
            mime='text/csv',
            key=f"download_csv_{usuario_instagram}"
        )
    
    with col2:
        if st.button("🤖 Análisis de Post Inteligente", type="primary", key="analysis_button"):
            # Preparar los datos para el análisis
            posts_data = []
            for _, post in df.iterrows():
                post_info = {
                    "likes": post[' Cantidad de Likes'] if ' Cantidad de Likes' in df.columns else 0,
                    "comments": post[' Cantidad de Comentarios'] if ' Cantidad de Comentarios' in df.columns else 0,
                    "caption": post[' Primer Comentario'] if ' Primer Comentario' in df.columns else "",
                    "hashtags": post[' Hashtags'] if ' Hashtags' in df.columns else "",
                    "fecha": post[' Fecha de Publicación'] if ' Fecha de Publicación' in df.columns else "",
                    "url": post[' URL del Post'] if ' URL del Post' in df.columns else ""
                }
                posts_data.append(post_info)
            
            try:
                with st.spinner("Realizando análisis inteligente..."):
                    # Realizar el análisis
                    results = analyze_instagram_posts(
                        posts_data=posts_data,
                        progress_callback=lambda msg: st.write(msg)
                    )
                    st.session_state.analysis_results = results
            except Exception as e:
                st.error(f"Error en el análisis inteligente: {str(e)}")
    
    # Mostrar resultados del análisis si existen
    if hasattr(st.session_state, 'analysis_results') and st.session_state.analysis_results:
        st.markdown("---")
        st.header("🤖 Resultados del Análisis Inteligente")
        
        results = st.session_state.analysis_results
        
        # Usar pestañas en lugar de expanders
        tab1, tab2, tab3 = st.tabs([
            "🎨 Análisis de Contenido",
            "💫 Análisis de Engagement",
            "🎯 Recomendaciones Estratégicas"
        ])
        
        with tab1:
            st.markdown(results['content_analysis'])
        
        with tab2:
            st.markdown(results['engagement_analysis'])
        
        with tab3:
            st.markdown(results['strategy_analysis'])
        
        # Botón para descargar todos los informes
        st.markdown("---")
        
        # Preparar el contenido del informe
        informe_completo = f"""
# ANÁLISIS INTELIGENTE DE INSTAGRAM

## 🎨 Análisis de Contenido
{results['content_analysis']}

## 💫 Análisis de Engagement
{results['engagement_analysis']}

## 🎯 Recomendaciones Estratégicas
{results['strategy_analysis']}
"""
        
        # Convertir el informe a bytes
        informe_bytes = informe_completo.encode()
        
        # Centrar el botón de descarga
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(
                label="📥 Descargar Informes Completos",
                data=informe_bytes,
                file_name="analisis_instagram_completo.md",
                mime="text/markdown",
                use_container_width=True,
                key=f"download_analysis_{usuario_instagram}"
            )

def otra_funcion():
    st.title("Otra Función")
    st.write("Aquí puedes añadir otra funcionalidad...")

def crear_cliente():
    st.markdown("<h1 style='color: #333333;'>Crear Nuevo Cliente</h1>", unsafe_allow_html=True)
    
    # Estilo para el formulario
    st.markdown("""
        <style>
        /* Estilos generales */
        .block-container {
            padding: 2rem;
            background-color: #ffffff;
        }
        
        /* Estilos para las secciones */
        .section-container {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .section-title {
            color: #1f77b4;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #1f77b4;
        }
        
        /* Estilos para los inputs */
        .stTextInput>div>div>input {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 0.5rem;
            font-size: 1rem;
            color: #333333;
        }
        
        .stTextInput label {
            color: #333333 !important;
        }
        
        /* Estilos para el textarea */
        .stTextArea>div>div>textarea {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 0.5rem;
            font-size: 1rem;
            color: #333333;
        }
        
        .stTextArea label {
            color: #333333 !important;
        }
        
        /* Estilos para el select */
        .stSelectbox>div>div>div {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            color: #333333;
        }
        
        .stSelectbox label {
            color: #333333 !important;
        }
        
        /* Estilos para el multiselect */
        .stMultiSelect>div>div>div {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            color: #333333;
        }
        
        .stMultiSelect label {
            color: #333333 !important;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.form("formulario_cliente"):
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        
        # Campos básicos
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del Cliente", 
                                 placeholder="Ej: Empresa S.L.")
        with col2:
            email = st.text_input("Email", 
                                placeholder="cliente@empresa.com")
        
        # Sector con opciones predefinidas
        sector = st.selectbox(
            "Sector",
            options=[
                "Tecnología",
                "Salud",
                "Educación",
                "Comercio",
                "Hostelería",
                "Construcción",
                "Servicios Profesionales",
                "Otro"
            ]
        )
        
        # Si selecciona "Otro", mostrar campo para especificar
        if sector == "Otro":
            sector_otro = st.text_input("Especifica el sector")
        
        # Descripción de la empresa
        descripcion = st.text_area(
            "Descripción de la empresa",
            placeholder="Breve descripción de la actividad y objetivos de la empresa...",
            height=100
        )
        
        # Accesos como multi-selección
        accesos = st.multiselect(
            "Accesos requeridos",
            options=[
                "Meta Business",
                "Acceso Web",
                "Manual de Marca",
                "Google (Analytics/Ads)",
                "Logo y recursos gráficos"
            ],
            default=None,
            help="Selecciona todos los accesos necesarios para este cliente"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón de envío
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            submitted = st.form_submit_button("Crear Cliente", 
                                           use_container_width=True,
                                           type="primary")
    
    # Procesar el formulario cuando se envía
    if submitted:
        if not nombre or not email:
            st.error("El nombre y email son campos obligatorios")
        else:
            datos_cliente = {
                "nombre": nombre,
                "email": email,
                "sector": sector_otro if sector == "Otro" else sector,
                "descripcion": descripcion,
                "accesos": accesos
            }
            
            st.success("Cliente creado correctamente")
            
            with st.expander("Ver detalles del cliente"):
                st.json(datos_cliente)

def crear_analisis():
    st.markdown("<h1 style='color: #333333;'>Crear Nuevo Análisis</h1>", unsafe_allow_html=True)
    
    # Estilo para el formulario
    st.markdown("""
        <style>
        /* Estilos generales */
        .block-container {
            padding: 2rem;
            background-color: #ffffff;
        }
        
        /* Estilos para las secciones */
        .section-container {
            background-color: #ffffff;
            padding: 2rem;
            border-radius: 10px;
            border: 1px solid #e0e0e0;
            margin-bottom: 2rem;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        
        .section-title {
            color: #1f77b4;
            font-size: 1.2rem;
            font-weight: 600;
            margin-bottom: 1.5rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #1f77b4;
        }
        
        /* Estilos para los inputs */
        .stTextInput>div>div>input {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 0.5rem;
            font-size: 1rem;
        }
        
        .stTextInput>div>div>input:focus {
            border-color: #1f77b4;
            box-shadow: 0 0 0 1px #1f77b4;
        }
        
        /* Estilos para los expansores */
        .streamlit-expanderHeader {
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
            padding: 1rem;
            margin-bottom: 0.5rem;
        }
        
        .streamlit-expanderHeader:hover {
            background-color: #f0f2f6;
        }
        
        /* Estilos para el multiselect */
        .stMultiSelect>div>div>div {
            background-color: #ffffff;
            border: 1px solid #e0e0e0;
            border-radius: 5px;
        }
        </style>
    """, unsafe_allow_html=True)
    
    with st.form("formulario_analisis"):
        # Sección Cliente
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📋 Información del Cliente</div>', 
                   unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            web_cliente = st.text_input("Web del cliente", 
                                      placeholder="www.ejemplo.com",
                                      help="Introduce la URL completa del sitio web")
        with col2:
            instagram_cliente = st.text_input("Usuario de Instagram", 
                                            placeholder="@usuario",
                                            help="Introduce el nombre de usuario sin @")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sección Competencia
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🎯 Análisis de Competencia</div>', 
                   unsafe_allow_html=True)
        
        tabs = st.tabs(["Competidor 1", "Competidor 2", "Competidor 3", "Competidor 4"])
        for i, tab in enumerate(tabs):
            with tab:
                col1, col2 = st.columns(2)
                with col1:
                    st.text_input("Web", 
                                key=f"web_comp_{i}",
                                placeholder="www.competidor.com",
                                help="URL del competidor")
                with col2:
                    st.text_input("Usuario de Instagram", 
                                key=f"insta_comp_{i}",
                                placeholder="@usuario",
                                help="Usuario de Instagram del competidor")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Sección Tipo de Informe
        st.markdown('<div class="section-container">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Tipo de Informe</div>', 
                   unsafe_allow_html=True)
        
        tipos_informe = st.multiselect(
            "Selecciona los tipos de análisis requeridos",
            options=[
                "Auditoría Redes Sociales",
                "Auditoría Web",
                "Auditoría SEO",
                "Informe Sectorial"
            ],
            default=None,
            help="Puedes seleccionar múltiples tipos de análisis"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Botón de envío con estilo específico
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            submitted = st.form_submit_button(
                "Crear Análisis", 
                use_container_width=True,
                type="primary"
            )
    
    # Procesar el formulario cuando se envía
    if submitted:
        if not web_cliente and not instagram_cliente:
            st.error("Debes proporcionar al menos una web o usuario de Instagram del cliente")
        elif not tipos_informe:
            st.error("Debes seleccionar al menos un tipo de informe")
        else:
            # Recopilar datos de competidores
            competidores = []
            for i in range(4):
                web = st.session_state.get(f"web_comp_{i}")
                insta = st.session_state.get(f"insta_comp_{i}")
                if web or insta:
                    competidores.append({
                        "web": web,
                        "instagram": insta
                    })
            
            datos_analisis = {
                "cliente": {
                    "web": web_cliente,
                    "instagram": instagram_cliente
                },
                "competidores": competidores,
                "tipos_informe": tipos_informe
            }
            
            st.success("Análisis creado correctamente")
            
            with st.expander("Ver detalles del análisis"):
                st.json(datos_analisis)

def cliente_conversacional():
    st.title("Cliente Conversacional 💬")
    
    chat_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Chat</title>
        <style>
            #chat-container {
                height: 700px;
                padding: 20px;
                background: white;
                border-radius: 10px;
            }
            .message-input {
                width: 80%;
                padding: 10px;
                margin: 10px 0;
            }
            .send-button {
                padding: 10px 20px;
                background: #1f77b4;
                color: white;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }
        </style>
    </head>
    <body>
        <div id="chat-container">
            <div id="messages"></div>
            <input type="text" id="userInput" class="message-input" placeholder="Escribe tu mensaje...">
            <button onclick="sendMessage()" class="send-button">Enviar</button>
        </div>

        <script>
            function sendMessage() {
                const input = document.getElementById('userInput');
                const message = input.value;
                if (message.trim() === '') return;

                // Mostrar mensaje del usuario
                const messagesDiv = document.getElementById('messages');
                messagesDiv.innerHTML += `<p><strong>Tú:</strong> ${message}</p>`;

                // Construir URL con el mensaje
                const webhookUrl = `HTTPS://marta-pro-n8n.onrender.com:443/webhook/85cff02e-b982-477d-8cdd-5fccf8dfed61?message=${encodeURIComponent(message)}`;
                
                // Realizar la petición GET con header de autorización
                fetch(webhookUrl, {
                    method: 'GET',
                    headers: {
                        'Authorization': 'Bearer n8n_api_c8b1cb5fde0d76c2a3930d2ca8b7'
                    }
                })
                .then(response => response.text())
                .then(response => {
                    console.log('Respuesta:', response);
                    messagesDiv.innerHTML += `<p><strong>Bot:</strong> ${response}</p>`;
                })
                .catch(error => {
                    console.error('Error:', error);
                    messagesDiv.innerHTML += `<p style="color: red;">Error al enviar el mensaje</p>`;
                });

                // Limpiar input
                input.value = '';
                
                // Scroll al final
                messagesDiv.scrollTop = messagesDiv.scrollHeight;
            }

            // Permitir enviar con Enter
            document.getElementById('userInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        </script>
    </body>
    </html>
    """
    
    st.components.v1.html(
        chat_html,
        height=800,
        scrolling=False
    )

def main():
    configurar_pagina()
    opcion = menu_lateral()
    
    # Manejar la navegación
    if opcion == "Inicio":
        pagina_inicio()
    elif opcion == "Subir Documento":
        subir_documento()
    elif opcion == "Enviar mail accesos":
        enviar_mail_accesos()
    elif opcion == "Análisis Instagram":
        analisis_instagram()
    elif opcion == "Crear Cliente":
        crear_cliente()
    elif opcion == "Crear Análisis":
        crear_analisis()
    elif opcion == "Design Agent":
        import design_agent_team
        design_agent_team.main()
    elif opcion == "Cliente Conversacional":
        cliente_conversacional()
    elif opcion == "Otra Función":
        otra_funcion()

if __name__ == "__main__":
    main() 