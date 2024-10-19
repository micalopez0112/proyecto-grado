from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routers.mapping import router as mapping_router
from app.routers.ontology import router as ontology_router
import uvicorn
from app.Coleccion_Películas.governance import connect_to_governanceDB
import json


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


#Descomentar para probar la generación del grafo de ColeccionPeliculas
driver = connect_to_governanceDB()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)