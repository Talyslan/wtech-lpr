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

        # 1. Baixar a imagem
        image = download_image(image_url)

        # 2. Pré-processar a imagem
        binary_image = preprocess_image(image)
        # Salvar a imagem processada para visualização
        processed_image = Image.fromarray(binary_image)
        processed_image.show()

        # 3. Reconhecer o texto na imagem processada
        recognized_text = recognize_text(binary_image)

        # 4. Converter imagem processada para base64
        binary_base64 = convert_to_base64(binary_image)

        return jsonify({
            'plate': recognized_text.strip(),
            'processed_image': binary_base64,
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def download_image(image_url):
    """Faz o download da imagem a partir de uma URL."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36"
    }
    image_response = requests.get(image_url, headers=headers)
    image_response.raise_for_status()  # Levanta um erro se a requisição falhar
    return Image.open(io.BytesIO(image_response.content))


def preprocess_image(image):
    """Pré-processa a imagem para reconhecimento de placa."""

    # Converter imagem para formato do OpenCV
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Redimensionar a imagem para melhorar a resolução
    img_cv = cv2.resize(img_cv, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

    # Converter para escala de cinza, necessário antes de aplicar a operação Black Hat
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)

    # Remover ruído inicial com um filtro de mediana aplicado no gray
    gray = cv2.medianBlur(gray, 1)

    # Aplicar operação Black Hat para melhorar os detalhes escuros
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)

    # Binarização com Otsu
    _, binary = cv2.threshold(blackhat, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Encontra componentes conectados para eliminar ruído adicional
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

    # Filtrar componentes pequenos e muito grandes que não se assemelham a caracteres
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        width = stats[i, cv2.CC_STAT_WIDTH]
        height = stats[i, cv2.CC_STAT_HEIGHT]

        # Limites de filtro para caracteres típicos (ajuste conforme necessário)
        if area < 50 or area > 700 or width > 100 or height > 100:
            binary[labels == i] = 0  # Remover componente não desejado

    # Encontrar contornos na imagem binária
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Encontrar a menor caixa delimitadora que engloba todos os caracteres detectados
    if contours:
        x, y, w, h = cv2.boundingRect(np.concatenate(contours))
        cropped_image = binary[y:y + h, x:x + w]  # Recorta a região da placa

        return cropped_image
    else:
        # Se nenhum contorno for encontrado, retornar a imagem binária original
        return binary


def recognize_text(binary_image):
    """Usa OCR para reconhecer o texto na imagem binária."""
    custom_config = r'--oem 3 --psm 7'
    # Executa o OCR
    text = pytesseract.image_to_string(binary_image, config=custom_config)
    # Limpeza adicional de espaços ou quebras de linha
    return text.strip()


def convert_to_base64(binary_image):
    """Converte a imagem binária para base64 em formato WEBP."""
    is_success, buffer = cv2.imencode('.webp', binary_image, [int(cv2.IMWRITE_WEBP_QUALITY), 40])
    return base64.b64encode(buffer).decode('utf-8')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)