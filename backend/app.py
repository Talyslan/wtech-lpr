from flask import Flask, request, jsonify
import cv2
import numpy as np
import requests
from PIL import Image
import io
import pytesseract  # Certifique-se de que o pytesseract está instalado
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)

# Rota para capturar imagem da câmera
@app.route('/capture', methods=['GET'])
def capture():
    try:
        username = 'admin'  # Substitua pelo seu nome de usuário
        password = 'Admin123'  # Substitua pela sua senha
        snapshot_url = 'http://192.168.0.11/Snapshot/1/RemoteImageCapture?ImageFormat=2'

        # Fazendo a requisição com autenticação básica
        response = requests.get(snapshot_url, auth=(username, password))
        response.raise_for_status()  # Levanta um erro se a requisição falhar

        # Lendo a imagem
        image = Image.open(io.BytesIO(response.content))
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Processar a imagem (exemplo de redimensionamento)
        img_cv = cv2.resize(img_cv, (640, 480))

        # Salvar a imagem se necessário, ou retornar diretamente
        _, img_encoded = cv2.imencode('.jpg', img_cv)
        return img_encoded.tobytes(), 200, {'Content-Type': 'image/jpeg'}

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para reconhecer texto em uma imagem
@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        # Espera um JSON contendo a URL da imagem
        data = request.get_json()
        image_url = data.get('image')

        if not image_url:
            return jsonify({'error': 'URL da imagem não fornecida'}), 400

        # Fazer o download da imagem
        image_response = requests.get(image_url)
        image_response.raise_for_status()  # Levanta um erro se a requisição falhar

        image = Image.open(io.BytesIO(image_response.content))

        # Usar pytesseract para reconhecer texto na imagem
        # Você pode ajustar o PSM (Page Segmentation Mode) conforme necessário
        text = pytesseract.image_to_string(image, config='--psm 8')  # PSM 8 trata a imagem como uma única linha

        # Processar e limpar o texto reconhecido
        recognized_text = text.strip()
        
        # Retornar o texto reconhecido
        return jsonify({'plate': recognized_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
