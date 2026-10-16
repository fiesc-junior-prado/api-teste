import cv2
import numpy as np

def draw_yolo_boxes(image_bytes: bytes, txt_content: str) -> bytes:
    # 1. Decodificar a imagem a partir dos bytes da requisição
    np_arr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    
    if img is None:
        raise ValueError("Não foi possível decodificar a imagem fornecida.")
    
    height, width, _ = img.shape
    
    # 2. Processar cada linha do arquivo TXT (formato: class_id x_center y_center w h)
    lines = txt_content.strip().split('\n')
    for line in lines:
        if not line.strip():
            continue
            
        parts = line.strip().split()
        if len(parts) >= 5:
            class_id = int(parts[0])
            x_center, y_center, w, h = map(float, parts[1:5])
            
            # Desnormalizar (converter de [0,1] para pixels)
            abs_w = int(w * width)
            abs_h = int(h * height)
            abs_x_center = int(x_center * width)
            abs_y_center = int(y_center * height)
            
            # Calcular os pontos x_min, y_min e x_max, y_max para o OpenCV
            x_min = int(abs_x_center - (abs_w / 2))
            y_min = int(abs_y_center - (abs_h / 2))
            x_max = int(abs_x_center + (abs_w / 2))
            y_max = int(abs_y_center + (abs_h / 2))
            
            # Configurações do desenho
            color = (0, 255, 0) # Verde em BGR
            thickness = 2
            
            # Desenhar o retângulo
            cv2.rectangle(img, (x_min, y_min), (x_max, y_max), color, thickness)
            
            # Desenhar o ID da classe logo acima da caixa
            text = f"cls: {class_id}"
            cv2.putText(img, text, (x_min, max(y_min - 5, 10)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)

    # 3. Codificar a imagem resultante de volta para bytes (JPEG)
    success, encoded_img = cv2.imencode('.jpg', img)
    if not success:
        raise ValueError("Erro ao codificar a imagem resultante.")
        
    return encoded_img.tobytes()