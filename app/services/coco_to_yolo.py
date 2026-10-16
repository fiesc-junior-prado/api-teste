import io
import zipfile
from collections import defaultdict
from app.models.schemas import CocoDataset

def convert_coco_to_yolo_zip(coco_data: CocoDataset) -> io.BytesIO:
    # 1. PREPARAÇÃO DOS DADOS
    # Cria um dicionário para aceder rapidamente às informações da imagem (largura e altura) através do seu ID.
    # Isto evita ter de pesquisar na lista de imagens para cada anotação (otimização de velocidade).
    images_map = {img.id: img for img in coco_data.images}
    
    # Agrupa todas as anotações associando-as ao ID da respetiva imagem.
    # O defaultdict garante que, se uma imagem não tiver anotações, devolve uma lista vazia em vez de dar erro.
    annotations_by_image = defaultdict(list)
    for ann in coco_data.annotations:
        annotations_by_image[ann.image_id].append(ann)
    
    # 2. CONFIGURAÇÃO DO FICHEIRO ZIP EM MEMÓRIA
    # Cria um espaço na memória RAM (um buffer de bytes) para guardar o ficheiro ZIP,
    # dispensando a necessidade e a lentidão de gravar no disco rígido do servidor.
    zip_buffer = io.BytesIO()
    
    # Abre o buffer como um ficheiro ZIP em modo de "append" (adicionar 'a'), aplicando compressão.
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        
        # 3. PROCESSAMENTO DE CADA IMAGEM
        for image_id, image_info in images_map.items():
            img_width = image_info.width
            img_height = image_info.height
            
            yolo_lines = [] # Lista para guardar as linhas de texto do ficheiro YOLO desta imagem
             
            # 4. CONVERSÃO MATEMÁTICA DAS ANOTAÇÕES (COCO -> YOLO)
            for ann in annotations_by_image.get(image_id, []):
                # O formato COCO guarda a caixa delimitadora (bbox) como coordenadas absolutas (em pixéis):
                # [ponto_x_minimo (canto superior esquerdo), ponto_y_minimo, largura_da_caixa, altura_da_caixa]
                x_min, y_min, bbox_w, bbox_h = ann.bbox
                class_id = ann.category_id
                
                # O formato YOLO exige coordenadas normalizadas (valores percentuais entre 0 e 1)
                # e aponta para o centro geométrico da caixa em vez do canto superior esquerdo:
                # [id_classe, x_centro, y_centro, largura, altura]
                
                # Calcula o centro da caixa somando metade da sua largura/altura ao ponto mínimo,
                # e divide pelas dimensões totais da imagem para obter a percentagem (normalização).
                x_center = (x_min + bbox_w / 2.0) / img_width
                y_center = (y_min + bbox_h / 2.0) / img_height
                
                # Normaliza também a largura e a altura totais da caixa
                norm_w = bbox_w / img_width
                norm_h = bbox_h / img_height
                
                # Clipping (Corte de Segurança): Garante que as coordenadas não ultrapassam 
                # os limites da imagem (0.0 até 1.0) devido a imprecisões na marcação original,
                # prevenindo assim erros fatais durante o treino do modelo YOLO.
                x_center = max(0.0, min(1.0, x_center))
                y_center = max(0.0, min(1.0, y_center))
                norm_w = max(0.0, min(1.0, norm_w))
                norm_h = max(0.0, min(1.0, norm_h))
                
                # Formata a linha com 6 casas decimais de precisão e adiciona à lista da imagem
                yolo_lines.append(f"{class_id} {x_center:.6f} {y_center:.6f} {norm_w:.6f} {norm_h:.6f}")
            
            # 5. GERAÇÃO E INSERÇÃO DO FICHEIRO DE TEXTO
            # Pega no nome original da imagem (ex: "gato_123.jpg") e substitui a extensão por ".txt" ("gato_123.txt")
            txt_filename = image_info.file_name.rsplit('.', 1)[0] + ".txt"
            
            # Junta todas as linhas processadas numa única string, separadas por quebras de linha (\n)
            txt_content = "\n".join(yolo_lines)
            
            # Escreve este conteúdo de texto diretamente num novo ficheiro txt dentro do nosso ZIP virtual
            zip_file.writestr(txt_filename, txt_content)
            
    # 6. FINALIZAÇÃO DO STREAMING
    # "Rebobina" o ponteiro de leitura do buffer de volta para a posição 0 (início absoluto).
    # Sem isto, o FastAPI leria a partir do final (onde a gravação parou) e enviaria um ficheiro ZIP com 0 bytes ao utilizador.
    zip_buffer.seek(0)
    
    return zip_buffer