# -*- coding: utf-8 -*-
"""
Motor de IA para OfficeAI
Maneja lógica de respuestas, Q-learning y toma de decisiones
"""
import unicodedata
from typing import List, Dict, Optional, Tuple

from config import FUZZY_CUTOFF, CORRECTION_PHRASES, MAX_CONTEXT_TURNS, MIN_RESULT_LENGTH, MAX_SYNTHESIS_LENGTH, AUTO_SAVE_WEB_ANSWERS, USE_GEMINI_SEARCH
from conversation_engine import ConversationEngine
from gemini_engine import GeminiEngine


class AIEngine:
    """Motor de inteligencia artificial del chatbot"""
    
    def __init__(self, database):
        self.db = database
        self.gemini_engine = GeminiEngine() if USE_GEMINI_SEARCH else None
        self.conversation_engine = ConversationEngine()
        self.last_question = None
        self.last_answer = None
        self.last_source = None
        self.last_learned_id = None  # ID de la última entrada aprendida
        self.conversation_context = []  # Almacena últimas conversaciones para contexto
        self.skipped_questions = set()  # Preguntas que no quieren ser evaluadas esta sesión
    
    def get_topic(self, question: str) -> str:
        """Detecta el tema de la pregunta"""
        q_lower = question.lower()
        
        topics = {
            "excel": ["excel", "hoja de cálculo", "fórmula", "celda", "tabla dinámica", "buscarv", "hoja", "cálculo"],
            "word": ["word", "procesador de textos", "estilos", "índice", "documento", "redactar"],
            "access": ["access", "base de datos", "tabla", "clave primaria", "consulta"],
            "powerpoint": ["powerpoint", "presentación", "diapositiva", "presentacion"],
            "outlook": ["outlook", "correo", "calendario", "reglas", "email"],
            "base_office": ["office", "microsoft office", "suite"]
        }
        
        for topic, keywords in topics.items():
            if any(keyword in q_lower for keyword in keywords):
                return topic
        
        return "general"
    
    def is_correction(self, text: str) -> bool:
        """Detecta si el texto es una corrección"""
        lower = text.lower()
        return any(phrase in lower for phrase in CORRECTION_PHRASES)
    
    def is_bad_answer(self, answer: str) -> bool:
        """Verifica si una respuesta es de baja calidad"""
        bad_phrases = ["no se", "quizas", "puede ser", "no tengo informacion", "no estoy seguro"]
        
        if len(answer.split()) < 2:
            return True
        
        for bp in bad_phrases:
            if bp in answer.lower():
                return True
        
        return False
    
    def find_answers(self, question: str) -> Optional[List[Dict]]:
        """Busca las mejores respuestas para una pregunta"""
        results = self.db.search_answers(question, limit=5)
        
        if results and not all(self.is_bad_answer(r['answer']) for r in results):
            good_results = [r for r in results if not self.is_bad_answer(r['answer'])]
            return good_results if good_results else None
        
        similar_questions = self.db.get_similar_questions(question, FUZZY_CUTOFF)
        
        if similar_questions:
            all_answers = []
            for similar_q in similar_questions:
                answers = self.db.search_answers(similar_q, limit=3)
                for ans in answers:
                    if not self.is_bad_answer(ans['answer']):
                        all_answers.append(ans)
            
            if all_answers:
                unique_answers = []
                seen = set()
                for ans in all_answers:
                    if ans['answer'] not in seen:
                        unique_answers.append(ans)
                        seen.add(ans['answer'])
                
                return unique_answers[:5]
        
        return None
    
    def handle_meta_questions(self, question: str) -> Optional[str]:
        """Maneja preguntas sobre el propio historial de conversación"""
        q = question.lower()
        normalized = unicodedata.normalize('NFKD', q).encode('ASCII', 'ignore').decode('utf-8')
        
        # Patrones para "qué te pregunté antes"
        if any(p in normalized for p in ["que te pregunte", "cual fue mi ultima", "que dije antes", "de que hablamos", "que pregunte"]):
            
            # Verificar contexto en memoria primero
            if self.conversation_context:
                last = self.conversation_context[-1]
                
                # Si la última en contexto es la actual (porque se añade al final), mirar la anterior
                if last['question'] == self.last_question and len(self.conversation_context) > 1:
                    last = self.conversation_context[-2]
                elif last['question'] == self.last_question:
                     return "Acabas de preguntarme eso precisamente."
                
                return f"Tu última pregunta fue: \"{last['question']}\". Y te respondí sobre: {last['answer'][:50]}..."
            
            # Si no hay contexto en memoria, buscar en DB
            history = self.db.get_history(limit=2)
            if len(history) > 1: # La 0 es la actual probablemente
                prev = history[1]
                return f"Anteriormente me preguntaste: \"{prev['question']}\"."
            
            return "No recuerdo que hayamos hablado de nada antes en esta sesión."
            
        return None

    def process_question(self, question: str) -> Tuple[Optional[str], str]:
        """Procesa una pregunta y devuelve la mejor respuesta"""
        self.last_question = question
        
        # 0. Verificar si es una intención puramente conversacional
        # 0. Verificar si es una intención puramente conversacional
        conv_response, intent = self.conversation_engine.process(question)
        
        # Si encuentra definición interna o es charla casual
        if conv_response:
            self.last_answer = conv_response
            self.last_source = 'conversational' # Puede ser 'DEFINITION_FOUND' también internamente
            return conv_response, 'conversational'
            
        # Si es intención técnica, seguimos al buscador
        # INTENT = intent (TECHNICAL o UNKNOWN)

        # 0.5. Verificar meta-preguntas (sobre el historial)
        meta_answer = self.handle_meta_questions(question)
        if meta_answer:
            self.last_answer = meta_answer
            self.last_source = 'meta_context'
            return meta_answer, 'meta'

        answers = self.find_answers(question)
        
        if answers:
            # Si la mejor respuesta tiene una confianza muy alta (ej. > 5), 
            # o si solo hay una y no está saltada, la damos directa.
            best_q = answers[0].get('q_value', 0)
            
            if len(answers) == 1 or best_q > 5.0:
                answer = answers[0]['answer']
                self.last_answer = answer
                self.last_source = 'local'
                
                self.db.update_q_value(question, answer, +0.5)
                self.db.add_to_history(question, answer, 'local')
                return answer, 'local'
            else:
                # Si hay varias con confianza similar, pedimos elegir
                self.last_answer = answers
                self.last_source = 'local_multi'
                return answers, 'local_multi'
        
        self.last_source = 'unknown'
        return None, 'unknown'
    
    def skip_question_feedback(self, question: str):
        """Marca una pregunta para no pedir feedback en esta sesión"""
        self.skipped_questions.add(self.db.normalize_text(question))
    
    def should_ask_feedback(self, question: str) -> bool:
        """Determina si se debe pedir feedback para esta pregunta"""
        return self.db.normalize_text(question) not in self.skipped_questions
    

    
    def search_web_and_process(self, question: str) -> Tuple[Optional[str], Optional[List[str]]]:
        """Realiza búsqueda web exclusivamente con Gemini"""
        
        if self.gemini_engine:
            answer, sources = self.gemini_engine.search_and_synthesize(question)
            if answer:
                self.last_source = 'gemini'
                self.last_answer = answer
                
                # Guardar automáticamente en knowledge base si está configurado
                if AUTO_SAVE_WEB_ANSWERS:
                    topic = self.get_topic(question)
                    self.last_learned_id = self.db.add_knowledge(question, answer, topic)
                    self.db.update_q_value(question, answer, +1.5)
                
                self.db.add_to_history(question, answer, 'gemini_search')
                return answer, sources
        
        return None, None
    
    def handle_user_correction(self, correct_answer: str, question: Optional[str] = None):
        """Maneja una corrección del usuario"""
        if question is None:
            question = self.last_question
        
        if not question:
            return False
        
        if isinstance(self.last_answer, str):
            self.db.update_q_value(question, self.last_answer, -2.0)
            self.db.record_selection(question, self.last_answer, was_correct=False)
        
        topic = self.get_topic(question)
        self.db.add_knowledge(question, correct_answer, topic)
        self.db.update_q_value(question, correct_answer, +2.0)
        self.db.add_to_history(question, correct_answer, 'user_correction', was_correct=True)
        
        return True
    
    def handle_answer_selection(self, question: str, selected_answer: str, is_correct: bool):
        """Maneja la selección de una respuesta por el usuario"""
        reward = +1.5 if is_correct else -0.5
        self.db.update_q_value(question, selected_answer, reward)
        self.db.record_selection(question, selected_answer, was_correct=is_correct)
        self.db.add_to_history(question, selected_answer, 'local', was_correct=is_correct)
    
    def add_alternative_answer(self, question: str, answer: str):
        """Añade una respuesta alternativa a una pregunta"""
        topic = self.get_topic(question)
        self.db.add_knowledge(question, answer, topic)
        self.db.update_q_value(question, answer, +1.0)
        self.db.add_to_history(question, answer, 'user_alternative')
    
    def add_to_context(self, question: str, answer: str):
        """Añade una interacción al contexto conversacional"""
        self.conversation_context.append({
            'question': question,
            'answer': answer
        })
        
        # Mantener solo las últimas N conversaciones
        if len(self.conversation_context) > MAX_CONTEXT_TURNS:
            self.conversation_context = self.conversation_context[-MAX_CONTEXT_TURNS:]
    
    def get_context_summary(self) -> str:
        """Obtiene un resumen del contexto conversacional"""
        if not self.conversation_context:
            return ""
        
        context_parts = []
        for ctx in self.conversation_context[-3:]:  # Últimas 3 interacciones
            context_parts.append(f"P: {ctx['question'][:50]}... R: {ctx['answer'][:50]}...")
        
        return " | ".join(context_parts)
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas del motor de IA"""
        db_stats = self.db.get_stats()
        
        return {
            **db_stats,
            'context_interactions': len(self.conversation_context)
        }

    def forget_last_interaction(self) -> str:
        """Olvida la última interacción aprendida si fue incorrecta"""
        if not self.last_learned_id:
            return "No tengo nada reciente que pueda olvidar."
        
        # Eliminar de base de conocimiento
        if self.db.delete_knowledge(self.last_learned_id):
            # Limpiar referencia
            self.last_learned_id = None
            
            # Limpiar de contexto también
            if self.conversation_context:
                self.conversation_context.pop()
                
            return "Entendido. He olvidado la última respuesta aprendida."
        else:
            return "Hubo un error al intentar olvidar la respuesta."
    def learn_from_url(self, url: str) -> bool:
        """Aprende de una URL específica proporcionada por el usuario"""
        try:
            import requests
            import re
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.8,en-US;q=0.5,en;q=0.3'
            }
            # Intentar primero con GET normal
            response = requests.get(url, headers=headers, timeout=12)
            if response.status_code != 200:
                print(f"[ERROR] URL returned status code {response.status_code}")
                return False
                
            # Extraer título
            title_search = re.search(r'<title>(.*?)</title>', response.text, re.IGNORECASE | re.DOTALL)
            title = title_search.group(1).strip() if title_search else "Información de URL"
            
            # Limpieza básica de HTML
            # 1. Eliminar scripts, estilos, comentarios
            text = re.sub(r'<(script|style|nav|footer|header).*?>.*?</\1>', '', response.text, flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r'<!--.*?-->', '', text, flags=re.DOTALL)
            
            # 2. Reemplazar tags comunes por espacios/newliness
            text = re.sub(r'<(p|br|div|li|h[1-6]).*?>', '\n', text, flags=re.IGNORECASE)
            
            # 3. Eliminar el resto de tags
            text = re.sub(r'<[^>]+>', ' ', text)
            
            # 4. Limpiar espacios
            lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 30]
            clean_text = '\n'.join(lines)
            
            if len(clean_text) < 100:
                print("[ERROR] No se pudo extraer suficiente texto relevante de la URL")
                return False
            
            # Sintetizar resultados para aprender
            # Como Gemini es ahora el único buscador, podríamos usarlo aquí también 
            # o mantener la extracción simple para PDFs/URLs manuales
            synthesis = clean_text[:MAX_SYNTHESIS_LENGTH]
            
            if synthesis:
                topic = self.get_topic(self.last_question)
                # Añadir como nuevo conocimiento
                self.db.add_knowledge(self.last_question, synthesis, topic)
                self.db.update_q_value(self.last_question, synthesis, +2.0)
                self.db.add_to_history(self.last_question, synthesis, 'user_url_correction', was_correct=True)
                return True
                
            return False
        except Exception as e:
            print(f"[ERROR] No se pudo aprender de la URL: {e}")
            return False
