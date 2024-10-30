from flask import Flask, request, jsonify
import cv2
import numpy as np
import requests
from PIL import Image
import io
from flask_cors import CORS 
import base64
import pytesseract 

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

# Rota para reconhecer placa da imagem
@app.route('/recognize', methods=['POST'])
def recognize():
    try:
        # Espera um JSON contendo a URL da imagem
        data = request.get_json()
        image_url = data.get('image')

        if not image_url:
            return jsonify({'error': 'URL da imagem não fornecida'}), 400
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
        }

        # Fazer o download da imagem
        image_response = requests.get(image_url, headers=headers)
        image_response.raise_for_status()  # Levanta um erro se a requisição falhar

        image = Image.open(io.BytesIO(image_response.content))

        # Pré-processamento da imagem
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        # 1. Redimensionar a imagem
        img_cv = cv2.resize(img_cv, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

        # 2. Converter para escala de cinza
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

        # 3. Binarização com Otsu
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # 4. Remover ruído
        binary = cv2.medianBlur(binary, 3)

        # Salvar a imagem processada para visualização
        processed_image = Image.fromarray(binary)
        processed_image.show()

        # 6. Processar e limpar o texto reconhecido
        custom_config = r'--oem 3 --psm 8'
        recognized_text = pytesseract.image_to_string(binary, config=custom_config)

        # Converter a imagem processada para WEBP para compressão superior
        is_success, buffer = cv2.imencode('.webp', binary, [int(cv2.IMWRITE_WEBP_QUALITY), 40])
        binary_base64 = base64.b64encode(buffer).decode('utf-8')

        return jsonify({
            'plate': recognized_text.strip(),
            'processed_image': binary_base64,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
