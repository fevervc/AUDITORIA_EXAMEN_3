# backend/main.py
import sqlite3
import re
import sys 
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal

# --- AÑADIDO: Importaciones para Monitorización ---
from prometheus_fastapi_instrumentator import Instrumentator
from loguru import logger

# LangChain
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_ollama.llms import OllamaLLM
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_core.runnables import RunnableBranch, RunnableLambda, RunnablePassthrough

# --- AÑADIDO: CONFIGURACIÓN DE LOGGING ESTRUCTURADO ---
logger.remove()
logger.add(sys.stdout, serialize=True, enqueue=True)

class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)
logging.getLogger("uvicorn").handlers = [InterceptHandler()]
logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]


# --- CONFIGURACIÓN Y MODELOS ---
VECTOR_STORE_DIR = "vector_store"
DB_PATH = "tickets.db"
app = FastAPI(title="Corporate EPIS Pilot API - Advanced Flow")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=False, allow_methods=["*"], allow_headers=["*"],
)

# --- AÑADIDO: INSTRUMENTACIÓN DE PROMETHEUS ---
Instrumentator().instrument(app).expose(app)


llm = OllamaLLM(model="smollm:360m", temperature=0, base_url="http://host.docker.internal:11434")
embeddings = HuggingFaceEmbeddings(model_name="intfloat/multilingual-e5-large")
vector_store = Chroma(persist_directory=VECTOR_STORE_DIR, embedding_function=embeddings)
retriever = vector_store.as_retriever()

# --- LÓGICA DE LANGCHAIN (MODIFICADA) ---
rag_prompt_template = "Usa el siguiente contexto para responder en español de forma concisa y útil a la pregunta.\nContexto: {context}\nPregunta: {question}\nRespuesta:"
rag_prompt = PromptTemplate.from_template(rag_prompt_template)
rag_chain = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff", retriever=retriever, chain_type_kwargs={"prompt": rag_prompt})

def create_support_ticket(description: str) -> str:
    """Crea un ticket de soporte y devuelve un mensaje de confirmación."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    problem_description = description.replace("ACTION_CREATE_TICKET:", "").strip()
    if not problem_description:
        problem_description = "Problema no especificado por el usuario."

    cursor.execute("INSERT INTO tickets (description, status) VALUES (?, ?)", (problem_description, "Abierto"))
    ticket_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return f"De acuerdo. He creado el ticket de soporte #{ticket_id} con tu problema: '{problem_description}'. El equipo técnico se pondrá en contacto contigo."

# El router ahora es más simple y robusto para smollm:360m
class RouteQuery(BaseModel):
    intent: Literal["pregunta_general", "reporte_de_problema", "despedida"] = Field(description="La intención del usuario.")

router_prompt = PromptTemplate(
    template="""Clasifica la pregunta del usuario en una de estas categorías:
'pregunta_general': El usuario pide información general o hace una pregunta (¿qué es?, ¿cómo?, información, servicios).
'reporte_de_problema': El usuario describe un fallo, error, problema técnico o algo que no funciona (no conecta, no enciende, da error).
'despedida': El usuario se despide, saluda o agradece (gracias, adiós, hola, chau, perfecto, ok).

Pregunta: {question}

Responde únicamente con la palabra correspondiente a la categoría elegida, sin rodeos, sin explicaciones y sin comillas:""",
    input_variables=["question"],
)

def parse_router_output(output_text: str) -> dict:
    text = output_text.lower().strip()
    if "reporte_de_problema" in text or "problema" in text or "error" in text or "fallo" in text or "falla" in text:
        return {"intent": "reporte_de_problema"}
    elif "despedida" in text or "gracias" in text or "adiós" in text or "adios" in text or "hola" in text or "chau" in text or "bye" in text or "ok" in text or "perfecto" in text:
        return {"intent": "despedida"}
    else:
        return {"intent": "pregunta_general"}

def pre_classify_and_route(input_dict: dict) -> dict:
    question = input_dict.get("question", "").lower().strip()
    saludos = {"hola", "gracias", "adiós", "adios", "chau", "chao", "bye", "gracia", "ok", "listo", "perfecto", "buenos dias", "buenas tardes"}
    if question in saludos or any(s in question for s in ["gracias", "muchas gracias", "adios", "hasta luego"]):
        return {"intent": "despedida"}
    
    prompt_val = router_prompt.format(question=question)
    try:
        response = llm.invoke(prompt_val)
        return parse_router_output(response)
    except Exception as e:
        logger.error(f"Error invocado en router LLM: {e}")
        return parse_router_output("pregunta_general")

router_chain = RunnableLambda(pre_classify_and_route)

chain_with_preserved_input = RunnablePassthrough.assign(decision=router_chain)

problem_chain = RunnableLambda(lambda x: {"query": x["question"]}) | rag_chain

# --- ENDPOINT DE LA API (MODIFICADO) ---
@app.get("/ask")
def ask_question(question: str):
    try:
        if question.startswith("ACTION_CREATE_TICKET:"):
            description = question.split(":", 1)[1]
            return {"answer": create_support_ticket(description), "follow_up_required": False}

        decision_result = chain_with_preserved_input.invoke({"question": question})
        intent = decision_result["decision"]["intent"]
        
        answer = ""
        follow_up = False

        if intent == "pregunta_general":
            result = problem_chain.invoke(decision_result)
            answer = result.get("result", "No se encontró respuesta.")
        elif intent == "reporte_de_problema":
            result = problem_chain.invoke(decision_result)
            solution = result.get("result", "No he encontrado una solución específica en mis documentos.")
            answer = f"{solution}\n\n¿Esta información soluciona tu problema?"
            follow_up = True
        # CAMBIO 3: Añadimos el manejo de la nueva intención
        elif intent == "despedida":
            answer = "De nada, ¡un placer ayudar! Si tienes cualquier otra consulta, aquí estaré. 😊"
            follow_up = False
            
        return {"answer": answer, "follow_up_required": follow_up}

    except Exception as e:
        # AÑADIDO: Usamos logger en lugar de print para un registro estructurado
        logger.error(f"Error en el endpoint /ask: {e}")
        return {"answer": "Lo siento, ha ocurrido un error.", "follow_up_required": False}