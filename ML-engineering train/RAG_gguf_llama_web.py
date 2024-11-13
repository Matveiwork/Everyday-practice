from flask import Flask, request, jsonify, render_template
from werkzeug.utils import secure_filename
import os
import faiss
import numpy as np
from llama_cpp import Llama
from sentence_transformers import SentenceTransformer

model_name = "MaziyarPanahi/Meta-Llama-3-8B-Instruct-GGUF"
model_file = "Meta-Llama-3-8B-Instruct.IQ1_M.gguf"
model_path = hf_hub_download(model_name, filename=model_file)

app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Инициализация моделей
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Модель для получения эмбеддингов
llm = Llama(model_path=model_path, n_ctx=16000, n_threads=8, n_gpu_layers=0)

# Глобальные переменные для базы знаний
document_texts = []
faiss_index = None

# Функция для обработки загруженных файлов
def process_uploaded_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    document_texts.append(text)
    embeddings = embedding_model.encode([text], convert_to_numpy=True)
    return embeddings

# Создание индекса FAISS
def create_faiss_index(embeddings):
    global faiss_index
    dimension = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimension)
    faiss_index.add(embeddings)

# Загрузка файла и обновление базы знаний
@app.route('/upload', methods=['POST'])
def upload_rag():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)

    # Обработка и обновление индекса
    embeddings = process_uploaded_file(file_path)
    create_faiss_index(embeddings)
    
    return jsonify({"message": "File uploaded and processed successfully"}), 200

# Поиск по базе знаний и генерация ответа
def search_and_generate_response(query, top_n=3):
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    distances, indices = faiss_index.search(query_embedding, top_n)
    retrieved_docs = [document_texts[i] for i in indices[0] if i != -1]
    context = "\n".join(retrieved_docs)
    response = llm(f"{context}\n{query}", max_tokens=100, temperature=0.7)
    return response['choices'][0]['text'].strip()

@app.route("/LLMA_rag", methods=["GET", "POST"])
def llama_rag():
    if request.method == "POST":
        user_input = request.form.get("message")
        if not user_input:
            return jsonify({"error": "No input provided"}), 400

        if faiss_index is None or not document_texts:
            return jsonify({"error": "Knowledge base is empty. Please upload a file first."}), 400

        response = search_and_generate_response(user_input)
        return jsonify({"response": response})

    return render_template("llama_rag.html")