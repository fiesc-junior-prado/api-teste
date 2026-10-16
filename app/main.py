import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import conversion, visualization, testes, classification, detection

# # Importação do serviço YOLO para pré-carregamento
# from app.services.yolo_inference import load_models, clear_models

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Executado no startup
#     try:
#         load_models()
#         yield
#     finally:
#         # Executado no shutdown
#         print("Limpando modelos da memória...")
#         clear_models()
# Inicialização da aplicação com o ciclo de vida associado
app = FastAPI(
    title="Computer Vision API",
    description="API para tarefas e utilitários de Visão Computacional",
    version="1.0.0",
    # lifespan=lifespan  # <-- Ciclo de vida adicionado aqui
)

# Inclusão das rotas
app.include_router(conversion.router, prefix="/api/v1", tags=["Conversão de Datasets"])
app.include_router(visualization.router, prefix="/api/v1", tags=["Visualização de Dados"])
# app.include_router(classification.router, prefix="/api/v1", tags=["Classificação de Imagens"])
# app.include_router(detection.router, prefix="/api/v1", tags=["Deteção de Objetos"])
# app.include_router(testes.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    # Configurações de inicialização do servidor Uvicorn
    # Nota: Quando se usa uvicorn.run diretamente no código com reload=True, 
    # é obrigatório passar a string de importação ("app.main:app") em vez da variável.
    import os
    port = int(os.environ.get("PORT", 10000))
    # E depois use: uvicorn.run(app, host="0.0.0.0", port=port)
    uvicorn.run(
        "app.main:app",       # Caminho para a instância do FastAPI (descomentado)
        host="0.0.0.0",       # Escuta em todas as interfaces de rede
        port=port,            # Porta padrão da aplicação
        reload=True,          # Ativa o live-reload (ideal para desenvolvimento)
        # workers=1,            # Número de processos (aumente em produção se não usar reload)
        # log_level="info"      # Nível de detalhamento dos logs
    )