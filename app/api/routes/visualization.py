from fastapi import APIRouter, File, UploadFile, HTTPException
from fastapi.responses import Response
from app.services.draw_bboxes import draw_yolo_boxes

router = APIRouter()

@router.post("/visualize/yolo", summary="Desenha bounding boxes YOLO em uma imagem")
async def visualize_yolo(
    image: UploadFile = File(..., description="Arquivo da imagem (jpg, png, etc)"),
    labels: UploadFile = File(..., description="Arquivo .txt com anotações YOLO")
):
    # Validação básica de tipo de arquivo
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo 'image' deve ser do tipo imagem.")
        
    try:
        # Lê os arquivos em memória
        img_bytes = await image.read()
        txt_bytes = await labels.read()
        
        # Converte os bytes do txt para string
        txt_content = txt_bytes.decode('utf-8')
        
        # Chama a função de serviço
        result_bytes = draw_yolo_boxes(img_bytes, txt_content)
        
        # Retorna a imagem final diretamente na resposta HTTP
        return Response(content=result_bytes, media_type="image/jpeg", headers={"Content-Disposition": f"inline; filename=visualized_{image.filename}"})
        # return Response(content=result_bytes, media_type="image/jpeg", headers={"Content-Disposition": f"attachment; filename=visualized_{image.filename}"})
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro interno ao processar a imagem: {str(e)}")