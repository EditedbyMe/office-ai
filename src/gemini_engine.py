# -*- coding: utf-8 -*-
"""
Motor de búsqueda con Gemini para OfficeAI
Utiliza Grounding with Google Search para respuestas precisas
"""
import google.generativeai as genai
from typing import Tuple, List, Optional
from config import GEMINI_API_KEY, GEMINI_MODEL

class GeminiEngine:
    """Maneja la integración con Google Gemini para búsqueda conectada a internet"""
    
    def __init__(self):
        self.api_key = GEMINI_API_KEY
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Herramienta de búsqueda de Google (Grounding)
            self.tools = [
                {'google_search_retrieval': {}}
            ]
            self.model = genai.GenerativeModel(
                model_name=GEMINI_MODEL,
                tools=self.tools
            )
        else:
            self.model = None

    def search_and_synthesize(self, question: str) -> Tuple[Optional[str], List[str]]:
        """
        Realiza una búsqueda conectada a internet usando Gemini y sintetiza la respuesta
        
        Returns:
            Tuple con (respuesta_sintetizada, lista_de_fuentes)
        """
        # No imprimir mensajes técnicos de búsqueda directamente al usuario
        
        # Crear prompt enfocado en Office y precisión
        prompt = (
            f"Actúa como un asistente experto llamado OfficeAI. "
            f"Responde a la siguiente pregunta de forma precisa y profesional: {question}. "
            f"Utiliza búsqueda en Google para asegurar que la información es actual y correcta. "
            f"IMPORTANTE: No incluyas frases de cierre como 'Espero que esta información te sea de utilidad' o similares. "
            f"Ve directamente al grano."
        )

        try:
            return self._generate_with_fallback(prompt)
        except Exception as e:
            print(f"[ERROR] Gemini Search falló definitivamente: {e}")
            return None, []

    def _generate_with_fallback(self, prompt: str) -> Tuple[str, List[str]]:
        """Intenta generar contenido con el modelo principal y un fallback si falla con 404"""
        try:
            response = self.model.generate_content(prompt)
            return self._parse_response(response)
        except Exception as e:
            if "429" in str(e):
                # Error de cuota: fallar silenciosamente aquí para que el controlador lo maneje
                # o reintentar sin herramientas
                model_no_tools = genai.GenerativeModel(model_name=GEMINI_MODEL)
                response = model_no_tools.generate_content(prompt)
                return self._parse_response(response)
                
            # Error 404: Modelo no encontrado
            if "404" in str(e):
                fallback_model = genai.GenerativeModel(
                    model_name="gemini-flash-latest",
                    tools=self.tools
                )
                response = fallback_model.generate_content(prompt)
                return self._parse_response(response)
            raise e

    def _parse_response(self, response) -> Tuple[str, List[str]]:
        """Extrae texto y fuentes de la respuesta de Gemini"""
        answer = response.text.strip()
        sources = []
        
        if hasattr(response, 'candidates') and response.candidates:
            candidate = response.candidates[0]
            if hasattr(candidate, 'grounding_metadata') and candidate.grounding_metadata:
                metadata = candidate.grounding_metadata
                
                # Método 1: grounding_chunks (URLs directas)
                if hasattr(metadata, 'grounding_chunks'):
                    for chunk in metadata.grounding_chunks:
                        if hasattr(chunk, 'web') and chunk.web.uri:
                            sources.append(chunk.web.uri)
                
                # Método 2: search_entry_point (HTML snippet con links)
                # (Opcional: extraer URLs del HTML si fuera necesario)
        
        return answer, list(set(sources))
