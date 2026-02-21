import sys
sys.path.insert(0, 'src')
from ai_engine import AIEngine
from database import Database
from search import WebSearch

# Mock DB and Web
db = Database()
web = WebSearch(db)
ai = AIEngine(db, web)

# 1. Simulate conversation context
print("1. Simulating conversation...")
ai.last_question = "pregunta actual"
ai.conversation_context = [
    {'question': '¿Qué es Excel?', 'answer': 'Excel es una hoja de cálculo...'},
    {'question': '¿Y Word?', 'answer': 'Word es un procesador de textos...'}
]

# 2. Ask meta question
print("2. Asking meta question: 'qué te pregunté antes'")
answer, source = ai.process_question("qué te pregunté antes")

print(f"Source: {source}")
print(f"Answer: {answer}")

if source == 'meta' and "Word" in answer:
    print("✅ SUCCESS: Correctly recalled last question")
else:
    print("❌ FAILURE: Did not recall correctly")

# 3. Ask another variant
print("\n3. Asking variant: 'cual fue mi ultima pregunta'")
answer, source = ai.process_question("cual fue mi ultima pregunta")
print(f"Answer: {answer}")

if source == 'meta' and "Word" in answer:
    print("✅ SUCCESS: Correctly recalled last question (variant)")
else:
    print("❌ FAILURE: Did not recall correctly (variant)")
