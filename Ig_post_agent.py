from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
import streamlit as st
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