import os
import cv2
import numpy as np
import tensorflow as tf

# Caminho dinâmico para o modelo
# Sobe apenas dois níveis (de tf_inference.py -> services -> app)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "api", "weights", "modelo_classificacao.keras")
# Carrega o modelo na memória apenas uma vez
modelo_tf = tf.keras.models.load_model(MODEL_PATH)

# Classes extraídas do seu treinamento CIFAR-10
CLASSES = {
    0: 'Avião', 1: 'Carro', 2: 'Pássaro', 3: 'Gato', 4: 'Cervo',
    5: 'Cachorro', 6: 'Sapo', 7: 'Cavalo', 8: 'Navio', 9: 'Caminhão'
}

def prever_imagem(image_bytes: bytes) -> dict:
    # 1. Decodificar a imagem recebida
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Imagem inválida ou corrompida.")
        
    # 2. Converter BGR (padrão OpenCV) para RGB (padrão TensorFlow)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # 3. Redimensionar para o formato do CIFAR-10 (32x32)
    img_resized = cv2.resize(img_rgb, (32, 32))
    
    # 4. Normalização idêntica ao treinamento (pixels de 0 a 1)
    img_normalized = img_resized / 255.0
    
    # 5. Adicionar a dimensão do batch. De (32, 32, 3) passa para (1, 32, 32, 3)
    img_array = np.expand_dims(img_normalized, axis=0)
    
    # Fazer a previsão
    previsoes = modelo_tf.predict(img_array)
    
    # Obter o índice da classe com maior probabilidade
    indice_classe = int(np.argmax(previsoes[0]))
    confianca = float(previsoes[0][indice_classe])
    
    return {
        "id_classe": indice_classe,
        "nome_classe": CLASSES.get(indice_classe, "Desconhecido"),
        "confianca": round(confianca * 100, 2)
    }