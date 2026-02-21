# -*- coding: utf-8 -*-
"""
Módulo de base de datos para OfficeAI
Usa SQLite para almacenamiento eficiente y persistente
"""
import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager
import unicodedata
import re

from config import DB_PATH, INITIAL_DATA


class Database:
    """Maneja todas las operaciones de base de datos"""
    
    def __init__(self, db_path: str = str(DB_PATH)):
        self.db_path = db_path
        self._initialize_db()
    
    @contextmanager
    def _get_connection(self):
        """Context manager para conexiones seguras"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _initialize_db(self):
        """Crea las tablas si no existen"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla de conocimiento
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS knowledge (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_normalized TEXT NOT NULL,
                    question_original TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(question_normalized, answer)
                )
            """)
            
            # Índices para búsquedas rápidas
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_question_normalized 
                ON knowledge(question_normalized)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_topic 
                ON knowledge(topic)
            """)
            
            # Tabla de Q-values para aprendizaje
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS q_values (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question_normalized TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    q_value REAL DEFAULT 0.0,
                    times_selected INTEGER DEFAULT 0,
                    times_correct INTEGER DEFAULT 0,
                    times_incorrect INTEGER DEFAULT 0,
                    last_used TIMESTAMP,
                    UNIQUE(question_normalized, answer)
                )
            """)
            
            # Tabla de historial
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    question TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    source TEXT NOT NULL,
                    was_correct BOOLEAN,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tabla de caché de búsquedas web
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS web_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query TEXT NOT NULL UNIQUE,
                    results TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP NOT NULL
                )
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_web_cache_query 
                ON web_cache(query)
            """)
            
            # Insertar datos iniciales si la DB está vacía
            cursor.execute("SELECT COUNT(*) FROM knowledge")
            if cursor.fetchone()[0] == 0:
                self._load_initial_data()
    
    def _load_initial_data(self):
        """Carga los datos iniciales en la base de datos"""
        print("[DB] Cargando datos iniciales...")
        for topic, questions in INITIAL_DATA.items():
            for question, answers in questions.items():
                for answer in answers:
                    self.add_knowledge(question, answer, topic)
        print(f"[DB] Datos iniciales cargados: {self.get_knowledge_count()} entradas")
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normaliza texto para comparaciones"""
        text = text.lower()
        text = unicodedata.normalize("NFD", text)
        text = "".join(c for c in text if unicodedata.category(c) != "Mn")
        text = re.sub(r"[^a-z0-9\s]", "", text)
        return re.sub(r"\s+", " ", text).strip()
    
    def add_knowledge(self, question: str, answer: str, topic: str) -> bool:
        """Añade nuevo conocimiento a la base de datos"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR IGNORE INTO knowledge 
                    (question_normalized, question_original, answer, topic)
                    VALUES (?, ?, ?, ?)
                """, (self.normalize_text(question), question, answer, topic))
                return cursor.lastrowid if cursor.rowcount > 0 else None
        except Exception as e:
            print(f"[ERROR] No se pudo añadir conocimiento: {e}")
            return None

    def delete_knowledge(self, knowledge_id: int) -> bool:
        """Elimina una entrada de conocimiento por ID"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM knowledge WHERE id = ?", (knowledge_id,))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"[ERROR] No se pudo eliminar conocimiento {knowledge_id}: {e}")
            return False
    
    def search_answers(self, question: str, limit: int = 5) -> List[Dict]:
        """Busca respuestas para una pregunta"""
        normalized_q = self.normalize_text(question)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT k.answer, k.topic, q.q_value, q.times_selected
                FROM knowledge k
                LEFT JOIN q_values q ON k.question_normalized = q.question_normalized 
                    AND k.answer = q.answer
                WHERE k.question_normalized = ?
                ORDER BY COALESCE(q.q_value, 0) DESC, q.times_selected DESC
                LIMIT ?
            """, (normalized_q, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'answer': row['answer'],
                    'topic': row['topic'],
                    'q_value': row['q_value'] or 0.0,
                    'times_selected': row['times_selected'] or 0
                })
            
            return results
    
    def get_similar_questions(self, question: str, similarity_threshold: float = 0.7) -> List[str]:
        """Encuentra preguntas similares usando matching fuzzy"""
        normalized_q = self.normalize_text(question)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT question_normalized FROM knowledge")
            
            similar = []
            for row in cursor.fetchall():
                stored_q = row['question_normalized']
                words_q = set(normalized_q.split())
                words_stored = set(stored_q.split())
                
                if not words_q or not words_stored:
                    continue
                
                intersection = len(words_q & words_stored)
                union = len(words_q | words_stored)
                similarity = intersection / union if union > 0 else 0
                
                if similarity >= similarity_threshold:
                    similar.append((stored_q, similarity))
            
            similar.sort(key=lambda x: x[1], reverse=True)
            return [q for q, _ in similar[:5]]
    
    def update_q_value(self, question: str, answer: str, reward: float):
        """Actualiza el Q-value para una respuesta"""
        normalized_q = self.normalize_text(question)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT q_value FROM q_values 
                WHERE question_normalized = ? AND answer = ?
            """, (normalized_q, answer))
            
            row = cursor.fetchone()
            current_q = row['q_value'] if row else 0.0
            new_q = current_q + reward
            
            cursor.execute("""
                INSERT INTO q_values (question_normalized, answer, q_value, last_used)
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(question_normalized, answer) DO UPDATE SET
                    q_value = ?,
                    last_used = CURRENT_TIMESTAMP
            """, (normalized_q, answer, new_q, new_q))
    
    def record_selection(self, question: str, answer: str, was_correct: bool):
        """Registra una selección de respuesta"""
        normalized_q = self.normalize_text(question)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if was_correct:
                cursor.execute("""
                    UPDATE q_values 
                    SET times_selected = times_selected + 1,
                        times_correct = times_correct + 1
                    WHERE question_normalized = ? AND answer = ?
                """, (normalized_q, answer))
            else:
                cursor.execute("""
                    UPDATE q_values 
                    SET times_selected = times_selected + 1,
                        times_incorrect = times_incorrect + 1
                    WHERE question_normalized = ? AND answer = ?
                """, (normalized_q, answer))
    
    def add_to_history(self, question: str, answer: str, source: str, was_correct: Optional[bool] = None):
        """Añade entrada al historial"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO history (question, answer, source, was_correct)
                VALUES (?, ?, ?, ?)
            """, (question, answer, source, was_correct))
    
    def get_history(self, limit: int = 20) -> List[Dict]:
        """Obtiene el historial reciente"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT question, answer, source, was_correct, timestamp
                FROM history
                ORDER BY timestamp DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def cache_web_results(self, query: str, results: List[Dict], ttl_hours: int = 24):
        """Cachea resultados de búsqueda web"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            expires_at = datetime.now().timestamp() + (ttl_hours * 3600)
            cursor.execute("""
                INSERT OR REPLACE INTO web_cache (query, results, expires_at)
                VALUES (?, ?, datetime(?, 'unixepoch'))
            """, (query, json.dumps(results), expires_at))
    
    def get_cached_web_results(self, query: str) -> Optional[List[Dict]]:
        """Obtiene resultados cacheados si no han expirado"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT results FROM web_cache
                WHERE query = ? AND expires_at > CURRENT_TIMESTAMP
            """, (query,))
            
            row = cursor.fetchone()
            if row:
                return json.loads(row['results'])
            return None
    
    def get_knowledge_count(self) -> int:
        """Obtiene el total de entradas de conocimiento"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM knowledge")
            return cursor.fetchone()['count']
    
    def get_stats(self) -> Dict:
        """Obtiene estadísticas de la base de datos"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            cursor.execute("SELECT COUNT(*) as count FROM knowledge")
            stats['total_knowledge'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(DISTINCT topic) as count FROM knowledge")
            stats['total_topics'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM history")
            stats['total_interactions'] = cursor.fetchone()['count']
            
            cursor.execute("SELECT COUNT(*) as count FROM web_cache")
            stats['cached_searches'] = cursor.fetchone()['count']
            
            return stats
    
    def export_to_json(self, filepath: str) -> bool:
        """Exporta toda la base de datos a JSON como respaldo"""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                export_data = {
                    'knowledge': [],
                    'history': [],
                    'q_values': [],
                    'exported_at': datetime.now().isoformat()
                }
                
                cursor.execute("SELECT * FROM knowledge")
                export_data['knowledge'] = [dict(row) for row in cursor.fetchall()]
                
                cursor.execute("SELECT * FROM history ORDER BY timestamp DESC LIMIT 100")
                export_data['history'] = [dict(row) for row in cursor.fetchall()]
                
                cursor.execute("SELECT * FROM q_values")
                export_data['q_values'] = [dict(row) for row in cursor.fetchall()]
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, ensure_ascii=False, indent=2, default=str)
                
                return True
        except Exception as e:
            print(f"[ERROR] No se pudo exportar a JSON: {e}")
            return False
