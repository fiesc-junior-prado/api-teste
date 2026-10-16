from fastapi import APIRouter, File, UploadFile, HTTPException
from app.services.tf_inference import prever_imagem

router = APIRouter()

@router.post("/classify", summary="Classifica o conteúdo de uma imagem usando TensorFlow")
async def classificar_imagem(file: UploadFile = File(...)):
    # Valida se é uma imagem
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="O arquivo enviado não é uma imagem válida.")
        
    try:
        # Lê os bytes do arquivo enviado
        image_bytes = await file.read()
        
        # Chama o modelo
        resultado = prever_imagem(image_bytes)
        
        return {
            "status": "sucesso",
            "arquivo": file.filename,
            "predicao": resultado
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro durante a inferência: {str(e)}")