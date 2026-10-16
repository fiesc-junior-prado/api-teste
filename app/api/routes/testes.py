from fastapi import APIRouter
from fastapi.responses import JSONResponse
from fastapi.responses import HTMLResponse
from fastapi.responses import PlainTextResponse

router = APIRouter( 
    prefix="/testes",
    tags=["Testes"]
)

@router.post("/jsonresponse", summary="Exemplo de retorno JSON com status 201")
def criar_projeto():
    dados = {"mensagem": "Projeto criado com sucesso!", "id": 123}
    
    # Retorna o JSON forçando o status HTTP 201 (Created)
    return JSONResponse(content=dados, status_code=201)

@router.get("/htmlresponse", response_class=HTMLResponse)
def painel_admin():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head><title>Painel da API</title></head>
        <body>
            <h1>Bem-vindo ao Painel de Controle</h1>
            <p>A API de Visão Computacional está online.</p>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)

@router.get("/plaintextresponse", response_class=PlainTextResponse)
def visualizar_logs():
    logs_brutos = "2026-10-09 10:00:01 INFO Iniciando worker...\n2026-10-09 10:05:00 WARN CPU acima de 80%."
    return PlainTextResponse(content=logs_brutos)

from fastapi.responses import RedirectResponse

@router.get("/redirectresponse", summary="Exemplo de redirecionamento para outra rota")
def redirecionar():
    # O status 301 indica que o recurso foi movido permanentemente
    # O status 307 ou 308 indicam redirecionamento temporário
    return RedirectResponse(url="/testes/chegar", status_code=301)

@router.get("/chegar", summary="Exemplo de redirecia")
def redirecionar():
    # O status 301 indica que o recurso foi movido permanentemente
    # O status 307 ou 308 indicam redirecionamento temporário
    return "Chguei"


from fastapi import Response

@router.get("/configuracao-xml")
def retornar_xml():
    xml_data = "<config><porta>8000</porta><debug>true</debug></config>"
    # Definindo um media_type personalizado que não tem uma classe pronta no FastAPI
    return Response(content=xml_data, media_type="application/xml")

@router.delete("/imagem/{id}")
def deletar_imagem(id: int):
    # Deleta a imagem do banco/disco...
    
    # Retorna HTTP 204 (No Content) indicando sucesso, mas sem nenhum corpo na resposta
    return Response(status_code=204)

# from fastapi import APIRouter
# from fastapi.responses import ORJSONResponse

# router = APIRouter()

# @router.get("/dados-pesados", response_class=ORJSONResponse)
# def gerar_dados_massivos():
#     # Simulando uma resposta com centenas de milhares de registros
#     dados_grandes = [{"id": i, "tag": "objeto"} for i in range(100000)]
    
#     # ORJSON é escrito em Rust e processa isso muito mais rápido que o JSON padrão do Python
#     return ORJSONResponse(content=dados_grandes)

from fastapi.responses import FileResponse
import os


@router.get("/download/peso-modelo")
def baixar_peso_yolo():
    caminho = "app/api/routes/conversion.py"
    
    if not os.path.exists(caminho):
        return {"erro": "Arquivo não encontrado"}
        
    return FileResponse(
        path=caminho,
        filename="meu_modelo.pt", # Nome que será sugerido no momento do download
        media_type="application/octet-stream" # Tipo binário genérico
    )

from fastapi.responses import StreamingResponse
import time

# Função geradora que usa o 'yield' em vez do 'return'
def gerador_de_relatorio():
    yield "Iniciando processamento...\n".encode("utf-8")
    time.sleep(1) # Simulando um trabalho demorado de 1 segundo
    
    yield "Analisando frame 1...\n".encode("utf-8")
    time.sleep(1)
    
    yield "Processo concluído!\n".encode("utf-8")

@router.get("/processar-video")
def streaming_processo():
    # O cliente vai recebendo as mensagens uma por uma a cada segundo, em tempo real
    return StreamingResponse(gerador_de_relatorio(), media_type="text/plain")