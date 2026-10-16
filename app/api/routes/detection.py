from fastapi import APIRouter, UploadFile, File, Query, HTTPException
from fastapi.responses import Response
from app.services.yolo_inference import predict_to_yolo_format
import os
router = APIRouter(prefix="/detection", tags=["Object Detection"])

@router.post("/detect", summary="Detecta objetos em uma imagem e retorna anotações no formato YOLO")
async def detect_objects(
    file: UploadFile = File(...),
    version: str = "v8" 
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Formato inválido. Envie uma imagem.")
    print(f"Recebido arquivo: {file.filename}, tipo: {file.content_type}, versão YOLO: {version}")
    try:
        # 1. Ler os bytes da imagem
        image_bytes = await file.read()
        
        # 2. Gerar o conteúdo do YOLO TXT usando a função do yolo_inference.py
        txt_content = predict_to_yolo_format(image_bytes, version)
        
        # 3. Extrair o nome original da imagem e trocar a extensão para .txt
        nome_original = file.filename
        nome_base = os.path.splitext(nome_original)[0]
        nome_txt = f"{nome_base}.txt"
        
        # 4. Retornar a resposta com o cabeçalho forçando o nome correto do arquivo
        return Response(
            content=txt_content,
            media_type="text/plain",
            headers={"Content-Disposition": f'attachment; filename="{nome_txt}"'}
        )
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no processamento: {str(e)}")