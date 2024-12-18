from flask import Flask, request, jsonify, render_template
from flask_wtf.csrf import CSRFProtect
import json
import os
import logging

# Создаем экземпляр Flask
app = Flask(__name__)
app.secret_key = 'df7a9fe7df150209544e62f8d1f2d5201e1385b7cb404bc90c24c966e2e10ec5'  # Замените на ваш секретный ключ
csrf = CSRFProtect(app)

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Файлы для хранения данных
data_file = 'chat_data.json'
pending_file = 'responses_pending.json'

# Функция для загрузки данных
def load_chat_data():
    if os.path.exists(data_file):
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Ошибка при загрузке данных: {e}")
            return {}
    else:
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return {}

# Функция для загрузки ожидающих ответов
def load_pending_data():
    if os.path.exists(pending_file):
        try:
            with open(pending_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            logger.error(f"Ошибка при загрузке ожидающих данных: {e}")
            return {}
    else:
        with open(pending_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return {}

chat_data = load_chat_data()
pending_data = load_pending_data()

# Функция для генерации ответов
def generate_response(user_message):
    user_message = user_message.lower()
    return chat_data.get(user_message, None)

@app.route('/')
def index():
    return render_template('chat.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '').strip()
    
    if not user_message:
        return jsonify({'response': "Пожалуйста, введите сообщение."}), 400

    logger.info(f"Получено сообщение от пользователя: {user_message}")
    bot_response = generate_response(user_message)

    if bot_response is None:
        # Если ответа нет, запрашиваем у пользователя
        return jsonify({'response': "Извините, я не понимаю. В моей базе нет ответа на ваш вопрос, ваш ответ отправлен на модерацию.", 'ask_for_answer': True})

    logger.info(f"Ответ бота: {bot_response}")
    return jsonify({'response': bot_response})

@app.route('/learn', methods=['POST'])
def learn():
    user_message = request.json.get('message', '').strip()
    user_answer = request.json.get('answer', '').strip()
    
    if user_message and user_answer:
        # Сохраняем ответ в файл ожидания
        pending_data[user_message.lower()] = user_answer
        
        # Сохраняем данные в файл ожидания
        try:
            with open(pending_file, 'w', encoding='utf-8') as f:
                json.dump(pending_data, f, ensure_ascii=False)
        except IOError as e:
            logger.error(f"Ошибка при сохранении данных: {e}")

        return jsonify({'response': "Спасибо! Я запомню это."}), 200
    
    return jsonify({'response': "Пожалуйста, предоставьте сообщение и ответ."}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
