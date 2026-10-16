from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from app.models.schemas import CocoDataset
from app.services.coco_to_yolo import convert_coco_to_yolo_zip

router = APIRouter()

@router.post("/convert/coco-to-yolo", summary="Converte JSON COCO para arquivos TXT YOLOv8 em ZIP")
def coco_to_yolo(payload: CocoDataset):
    zip_buffer = convert_coco_to_yolo_zip(payload)
    
    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
           headers={"Content-Disposition": "attachment; filename=yolo_annotations.zip"}
    )