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

        # Pré-processamento da imagem
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # Convertendo para escala de cinza
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # Aplicando um desfoque para suavizar a imagem
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Aplicando binarização para melhorar a detecção de texto
        _, binary = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Usar pytesseract para reconhecer texto na imagem
        # Ajustando o PSM e OCR Engine Mode conforme necessário
        custom_config = r'--oem 3 --psm 8'  # OEM 3 usa o modo padrão de OCR e PSM 8 trata a imagem como uma única linha
        text = pytesseract.image_to_string(binary, config=custom_config)

        # Processar e limpar o texto reconhecido
        recognized_text = text.strip()

        # Retornar o texto reconhecido
        return jsonify({'plate': recognized_text})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
