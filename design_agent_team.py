from agno.agent import Agent
from agno.models.google import Gemini
from agno.tools.duckduckgo import DuckDuckGoTools
import streamlit as st
from PIL import Image
from typing import List, Optional
import base64
from io import BytesIO

# API Key fija
GEMINI_API_KEY = "AIzaSyBa5Rp_1wlQ73FNCbotBoPXxzZImz5q5Hg"  # Reemplaza esto con tu API key real

def initialize_agents() -> tuple[Agent, Agent, Agent]:
    try:
        model = Gemini(id="gemini-2.0-flash-exp", api_key=GEMINI_API_KEY)
        
        vision_agent = Agent(
            model=model,
            instructions=[
                "Eres un experto en análisis visual que:",
                "1. Identifica elementos de diseño, patrones y jerarquía visual",
                "2. Analiza esquemas de colores, tipografía y diseño de la web",
                "3. Detecta componentes de la interfaz de usuario y sus relaciones",
                "4. Evalúa la consistencia visual y el branding",
                "Se específico y técnico en tu análisis"
            ],
            markdown=True
        )

        ux_agent = Agent(
            model=model,
            instructions=[
                "Eres un experto en análisis de experiencia de usuario que:",
                "1. Evalúa flujos de usuario y patrones de interacción",
                "2. Identifica problemas de usabilidad y oportunidades",
                "3. Sugerencia mejoras de UX basadas en las mejores prácticas",
                "4. Analiza accesibilidad y diseño inclusivo",
                "Enfoque en insights de usuario y mejoras prácticas"
            ],
            markdown=True
        )

        market_agent = Agent(
            model=model,
            tools=[DuckDuckGoTools()],
            instructions=[
                "Eres un experto en investigación de mercado que:",
                "1. Identifica tendencias de mercado y patrones de competidores",
                "2. Analiza productos similares y características",
                "3. Sugerencia posicionamiento de mercado y oportunidades",
                "4. Proporciona insights específicos del sector",
                "Enfoque en inteligencia de mercado accionable"
            ],
            markdown=True
        )
        
        return vision_agent, ux_agent, market_agent
    except Exception as e:
        st.error(f"Error initializing agents: {str(e)}")
        return None, None, None

def create_analysis_doc(vision_response=None, ux_response=None, market_response=None, context=None, elements=None):
    # Crear el contenido del archivo de texto
    content = []
    
    # Título
    content.append("ANÁLISIS DE DISEÑO WEB")
    content.append("=" * 20 + "\n")
    
    # Contexto y elementos analizados
    if context:
        content.append("CONTEXTO")
        content.append("-" * 10)
        content.append(context + "\n")
    
    if elements:
        content.append("ELEMENTOS ANALIZADOS")
        content.append("-" * 10)
        content.append(', '.join(elements) + "\n")
    
    # Añadir respuestas de los agentes
    if vision_response:
        content.append("ANÁLISIS DE DISEÑO VISUAL")
        content.append("-" * 10)
        content.append(vision_response + "\n")
    
    if ux_response:
        content.append("ANÁLISIS DE EXPERIENCIA DE USUARIO")
        content.append("-" * 10)
        content.append(ux_response + "\n")
    
    if market_response:
        content.append("ANÁLISIS DE MERCADO")
        content.append("-" * 10)
        content.append(market_response + "\n")
    
    # Guardar en memoria
    doc_io = BytesIO()
    doc_io.write('\n'.join(content).encode('utf-8'))
    doc_io.seek(0)
    return doc_io

def main():
    st.title("Equipo de agentes de análsis diseño")
    
    vision_agent, ux_agent, market_agent = initialize_agents()
    
    if all([vision_agent, ux_agent, market_agent]):
        # File Upload Section
        st.header("📤 Sube los Screeshot de la web del cliente")
        col1, space, col2 = st.columns([1, 0.1, 1])
        
        with col1:
            design_files = st.file_uploader(
                "Upload UI/UX Designs",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                key="designs"
            )
            
            if design_files:
                for file in design_files:
                    image = Image.open(file)
                    st.image(image, caption=file.name, use_container_width=True)

        with col2:
            competitor_files = st.file_uploader(
                "Upload Competitor Designs (Optional)",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=True,
                key="competitors"
            )
            
            if competitor_files:
                for file in competitor_files:
                    image = Image.open(file)
                    st.image(image, caption=f"Competitor: {file.name}", use_container_width=True)

        # Analysis Configuration
        st.header("🎯 Configuración del análisis")

        analysis_types = st.multiselect(
            "Selecciona los tipos de análisis",
            ["Diseño visual", "Experiencia de usuario", "Análisis de mercado"],
            default=["Diseño visual"]
        )

        specific_elements = st.multiselect(
            "Áreas de enfoque",
            ["Esquema de colores", "Tipografía", "Diseño de la web", "Interacciones", 
             "Accesibilidad", "Branding", "Alineación de la web"]
        )

        context = st.text_area(
            "Contexto adicional",
            placeholder="Describe tu producto, audiencia objetivo o preocupaciones específicas..."
        )

        # Analysis Process
        if st.button("🚀 Ejecutar análisis", type="primary"):
            if design_files:
                try:
                    st.header("📊 Resultados del análisis")
                    
                    # Variables para almacenar las respuestas
                    vision_response = None
                    ux_response = None
                    market_response = None
                    
                    # Process images once
                    def process_images(files):
                        processed_images = []
                        for file in files:
                            try:
                                # Leer el archivo como bytes
                                image_bytes = file.read()
                                
                                # Convertir a base64
                                image_base64 = base64.b64encode(image_bytes).decode('utf-8')
                                
                                # Crear el diccionario con el formato correcto
                                image_data = {
                                    "content": image_base64,
                                    "mime_type": f"image/{file.type.split('/')[-1]}"
                                }
                                
                                processed_images.append(image_data)
                                
                                # Resetear el puntero del archivo para poder usarlo después
                                file.seek(0)
                                
                            except Exception as e:
                                st.error(f"Error procesando imagen {file.name}: {str(e)}")
                                continue
                        return processed_images
                    
                    design_images = process_images(design_files)
                    competitor_images = process_images(competitor_files) if competitor_files else []
                    all_images = design_images + competitor_images
                    
                    # Visual Design Analysis
                    if "Diseño visual" in analysis_types and design_files:
                        with st.spinner("🎨 Analizando diseño visual..."):
                            if all_images:
                                vision_prompt = f"""
                                Analiza estos diseños enfocándote en: {', '.join(specific_elements)}
                                Contexto adicional: {context}
                                Proporciona insights específicos sobre elementos de diseño visual.
                                
                                Por favor, formatea tu respuesta con encabezados claros y puntos de viñeta.
                                Enfoque en observaciones concretas y insights accionables.
                                """
                                
                                response = vision_agent.run(
                                    message=vision_prompt,
                                    images=all_images
                                )
                                
                                vision_response = response.content
                                st.subheader("🎨 Análisis de diseño visual")
                                st.markdown(vision_response)
                    
                    # UX Analysis
                    if "Experiencia de usuario" in analysis_types:
                        with st.spinner("🔄 Analizando experiencia de usuario..."):
                            if all_images:
                                ux_prompt = f"""
                                Evalúa la experiencia de usuario considerando: {', '.join(specific_elements)}
                                Contexto adicional: {context}
                                Enfoque en flujos de usuario, interacciones y accesibilidad.
                                
                                Por favor, formatea tu respuesta con encabezados claros y puntos de viñeta.
                                Enfoque en observaciones concretas y mejoras accionables.
                                """
                                
                                response = ux_agent.run(
                                    message=ux_prompt,
                                    images=all_images
                                )
                                
                                ux_response = response.content
                                st.subheader("🔄 Análisis de experiencia de usuario")
                                st.markdown(ux_response)
                    
                    # Market Analysis
                    if "Análisis de mercado" in analysis_types:
                        with st.spinner("📊 Conduciendo análisis de mercado..."):
                            market_prompt = f"""
                            Analiza el posicionamiento de mercado y tendencias basadas en estos diseños.
                            Contexto: {context}
                            Compara con diseños de competidores si se proporciona.
                            Sugerencia oportunidades de mercado y posicionamiento.
                            
                            Por favor, formatea tu respuesta con encabezados claros y puntos de viñeta.
                            Enfoque en insights de mercado concretos y recomendaciones accionables.
                            """
                            
                            response = market_agent.run(
                                message=market_prompt,
                                images=all_images
                            )
                            
                            market_response = response.content
                            st.subheader("📊 Análisis de mercado")
                            st.markdown(market_response)
                    
                    # Combined Insights
                    if len(analysis_types) > 1:
                        st.subheader("🎯 Key Takeaways")
                        st.info("""
                        Arriba encontrarás un análisis detallado de múltiples agentes de IA especializados, cada uno enfocado en su área de expertise:
                        - Agente de diseño visual: Analiza elementos de diseño y patrones
                        - Agente de experiencia de usuario: Evalúa la experiencia de usuario y interacciones
                        - Agente de investigación de mercado: Proporciona contexto de mercado y oportunidades
                        """)
                    
                    # Botón de descarga
                    if any([vision_response, ux_response, market_response]):
                        doc_io = create_analysis_doc(
                            vision_response=vision_response,
                            ux_response=ux_response,
                            market_response=market_response,
                            context=context,
                            elements=specific_elements
                        )
                        
                        st.download_button(
                            label="📥 Descargar Análisis Completo (TXT)",
                            data=doc_io,
                            file_name="analisis_diseno_web.txt",
                            mime="text/plain"
                        )
                
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
            else:
                st.warning("Por favor, sube al menos un diseño para analizar.")
    else:
        st.error("Error al inicializar los agentes. Por favor, verifica la API key y vuelve a intentarlo.")

# Footer with usage tips
st.markdown("---")
st.markdown("""
<div style='text-align: center'>
    <h4>Tips for Best Results</h4>
    <p>
    • Upload clear, high-resolution images<br>
    • Include multiple views/screens for better context<br>
    • Add competitor designs for comparative analysis<br>
    • Provide specific context about your target audience
    </p>
</div>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main() 