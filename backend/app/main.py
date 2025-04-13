from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles

from app.routers.mapping import router as mapping_router
from app.routers.ontology import router as ontology_router
from app.routers.schema import router as schema_router
from app.routers.dataquality import router as dataquality_router
from app.repositories.metadata_repo import init_governance_zone
from app.repositories.metadata.repository import MetadataRepository

import uvicorn

import http.server
import socketserver
import threading

origins = ['http://localhost:3000']

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mapping_router, prefix="/mapping", tags=["mappings"])
app.include_router(ontology_router, prefix="/ontologies", tags=["ontologies"])
app.include_router(schema_router, prefix="/schemas", tags=["schemas"])
app.include_router(dataquality_router, prefix="/data-quality", tags=["data-quality"])



def start_owl_server(port=8001, directory="./upload/ontologies"):

    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=directory, **kwargs)

    with ReusableTCPServer(("", port), CustomHTTPRequestHandler) as httpd:
        print(f"Se puede acceder a la ontología de dominio .owl bajo: http://127.0.0.1:{port}/nombre_ontologia.owl")
        httpd.serve_forever()
        ##queda publica la ontología en http://127.0.0.1:8001/movie_ootest.owl
#Se levanta server que publique la ontología para acceder a través de URI
thread = threading.Thread(target=start_owl_server, daemon=True)
thread.start()

repo = MetadataRepository()
repo.init_governance_zone()



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)