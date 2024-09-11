from flask import Flask, render_template, request, session, jsonify, redirect, url_for, Blueprint
from conexion import app, mongo, login, logout, register  # Importamos las rutas de autenticación
import google.generativeai as genai
import os
from gemini.promts import instruccion2, instruccion3
from markupsafe import Markup
import re
import markdown2
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from bson.objectid import ObjectId

chatbot = Blueprint('chatbot', __name__)

generation_config = {
    "temperature": 0.7,  # Reducida para respuestas más concisas
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 1024,  # Reducido significativamente
}

safety_settings = [
    {"category": "HARM_CATEGORY_DANGEROUS", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(model_name="gemini-1.5-flash",
                              generation_config=generation_config,
                              safety_settings=safety_settings)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Configuración de FAISS y embeddings
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)

# Inicialización del chat y configuraciones
global chat
chat = model.start_chat(history=[])
instruction = instruccion2
MAX_HISTORY = 8

app = Flask(__name__, static_folder='./templates')
app.secret_key = '1'

def format_response(text):
    html = markdown2.markdown(text)
    html = re.sub(r'\*\*?', '', html)
    html = re.sub(r'<ul>\s*((?:<li>.*?</li>\s*)+)</ul>', r'<div class="single-list">\1</div>', html, flags=re.DOTALL)
    html = re.sub(r'^\s*- ', '• ', html, flags=re.MULTILINE)
    return html

def clean_text(text):
    cleaned_text = re.sub(r'<[^>]+>|\*|#', '', text)
    return cleaned_text

def update_conversation_history(history, user_input, bot_response):
    history.append({"role": "user", "content": user_input})
    history.append({"role": "assistant", "content": bot_response})
    return history[-MAX_HISTORY*2:]

def reset_conversation():
    global chat
    chat = model.start_chat(history=[])
    session['conversation_history'] = []

@chatbot.route('/app1', methods=['GET', 'POST'])
def app1():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'GET':
        user = mongo.db.datos_usuarios.find_one({'_id': ObjectId(session['user_id'])})
        reset_conversation()
        return render_template('app1.html', user=user, conversations=[])
    elif request.method == 'POST':
        question = request.form['question'].lower()
        
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        
        if 'morro' in question or 'marc' in question or 'canñlkj' in question:
            response_message = """ <div><p>Te comparto el temario del curso <strong>"IA Generativa y Disrupción Digital en los Negocios"</strong> impartido por EGADE.</p>..."""  # Contenido omitido por brevedad
            session['conversation_history'] = update_conversation_history(
                session['conversation_history'], question, response_message)
            session.modified = True
            return jsonify({'response': [Markup(response_message)]})
        
        # Usando FAISS para recuperar contexto relevante
        docs = vector_store.similarity_search(question, k=3)  # Reducido de 3 a 2
        context = "\n".join([doc.page_content for doc in docs])
        
        full_prompt = f"{instruccion2}\n\nContext:\n{context}\n\nConversation history:\n"
        for entry in session['conversation_history'][-2:]:  # Solo las últimas 2 entradas
            full_prompt += f"{entry['role']}: {entry['content']}\n"
        full_prompt += f"user: {question}\nassistant:"
        
        response = chat.send_message(full_prompt)
        bot_response = response.text
        
        print(f"System Instruction:\n{full_prompt}")
        print(f"Question: {question}")
        print(f"Response: {bot_response}")
        
        session['conversation_history'] = update_conversation_history(
            session['conversation_history'], question, bot_response)
        
        # Estimate token counts

        

        
        formatted_response = format_response(bot_response)
        response_lines = [Markup(line) for line in formatted_response.split('\n') if line.strip()]
        
        session.modified = True
        return jsonify({
            'response': response_lines,

        })

@chatbot.route('/app2', methods=['GET', 'POST'])
def app2():
    if request.method == 'GET':
        user = mongo.db.datos_usuarios.find_one({'_id': ObjectId(session['user_id'])})
        reset_conversation()
        return render_template('app2.html', user=user, conversations=[])
    elif request.method == 'POST':
        question = request.form['question'].lower()
        
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        
        if 'morro' in question or 'marc' in question or 'canñlkj' in question:
            response_message = """ <div><p>Te comparto el temario del curso <strong>"IA Generativa y Disrupción Digital en los Negocios"</strong> impartido por EGADE.</p>..."""  # Contenido omitido por brevedad
            session['conversation_history'] = update_conversation_history(
                session['conversation_history'], question, response_message)
            session.modified = True
            return jsonify({'response': [Markup(response_message)]})
        
        # Usando FAISS para recuperar contexto relevante
        docs = vector_store.similarity_search(question, k=3)  # Reducido de 3 a 2
        context = "\n".join([doc.page_content for doc in docs])
        
        full_prompt = f"{instruccion3}\n\nContext:\n{context}\n\nConversation history:\n"
        for entry in session['conversation_history'][-2:]:  # Solo las últimas 2 entradas
            full_prompt += f"{entry['role']}: {entry['content']}\n"
        full_prompt += f"user: {question}\nassistant:"
        
        response = chat.send_message(full_prompt)
        bot_response = response.text
        
        print(f"System Instruction:\n{full_prompt}")
        print(f"Question: {question}")
        print(f"Response: {bot_response}")
        
        session['conversation_history'] = update_conversation_history(
            session['conversation_history'], question, bot_response)
        
        # Estimate token counts

        

        
        formatted_response = format_response(bot_response)
        response_lines = [Markup(line) for line in formatted_response.split('\n') if line.strip()]
        
        session.modified = True
        return jsonify({
            'response': response_lines,

        })

@chatbot.route('/chat', methods=['POST'])
def chat():
    question = request.form['question'].lower()
    app_version = request.form['app_version']
    
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'GET':
        user = mongo.db.datos_usuarios.find_one({'_id': ObjectId(session['user_id'])})
        reset_conversation()
        return render_template('index.html', user=user, conversations=[])

    elif request.method == 'POST':
        question = request.form['question'].lower()
        
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        
        if 'morro' in question or 'marc' in question or 'canñlkj' in question:
            response_message = """ <div><p>Te comparto el temario del curso <strong>"IA Generativa y Disrupción Digital en los Negocios"</strong> impartido por EGADE.</p>..."""  # Contenido omitido por brevedad
            session['conversation_history'] = update_conversation_history(
                session['conversation_history'], question, response_message)
            session.modified = True
            return jsonify({'response': [Markup(response_message)]})
        
        # Usando FAISS para recuperar contexto relevante
        docs = vector_store.similarity_search(question, k=3)  # Reducido de 3 a 2
        context = "\n".join([doc.page_content for doc in docs])
        
        full_prompt = f"{instruccion2}\n\nContext:\n{context}\n\nConversation history:\n"
        for entry in session['conversation_history'][-2:]:  # Solo las últimas 2 entradas
            full_prompt += f"{entry['role']}: {entry['content']}\n"
        full_prompt += f"user: {question}\nassistant:"
        
        response = chat.send_message(full_prompt)
        bot_response = response.text
        
        print(f"System Instruction:\n{full_prompt}")
        print(f"Question: {question}")
        print(f"Response: {bot_response}")
        
        session['conversation_history'] = update_conversation_history(
            session['conversation_history'], question, bot_response)
        
        # Estimate token counts
        input_tokens = estimate_token_count(full_prompt)
        output_tokens = estimate_token_count(bot_response)
        
        print("Estimated Input tokens:", input_tokens)
        print("Estimated Output tokens:", output_tokens)
        
        formatted_response = format_response(bot_response)
        response_lines = [Markup(line) for line in formatted_response.split('\n') if line.strip()]
        
        session.modified = True
        return jsonify({
            'response': response_lines,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens
        })
    return render_template('app1.html', user=user, conversations=[])