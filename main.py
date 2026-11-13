from datetime import datetime
from typing import List

from bson import ObjectId
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from database import coleccion_citas, verificar_conexion
from models import Cita, CitaCreate, CitaUpdate

app = FastAPI(
    title="API PARA SERVICIOS DE SPA",
    description="API RESTful asincrona con FastAPI y MongoDB (FARM Stack).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_db_client():
    await verificar_conexion()


@app.get("/", tags=["Raíz"])
async def root():
    return {
        "mensaje": "Bienvenido al servicio de agendamiento para servicios de spa.",
        "documentation": "/docs",
    }


@app.get(
    "/citas",
    response_model=List[Cita],
    status_code=status.HTTP_200_OK,
    tags=["Citas"],
    summary="Obtener todas las citas registradas",
)
async def get_todas_las_citas():
    # Convertimos el cursor de MongoDB a una lista de Python
    citas = await coleccion_citas.find().to_list(length=100)
    return citas


@app.post(
    "/citas",
    response_model=Cita,
    status_code=status.HTTP_201_CREATED,
    tags=["Citas"],
    summary="Crear una nueva cita en MongoDB",
)
async def create_cita(cita_in: CitaCreate):
    cita_existente = await coleccion_citas.find_one({"cliente": cita_in.cliente})
    if cita_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe una cita registrada con el id '{cita_in.cliente}'.",
        )
    nueva_cita = cita_in.model_dump()
    nueva_cita["fecha_creacion"] = datetime.now()

    resultado = await coleccion_citas.insert_one(nueva_cita)

    cita_creada = await coleccion_citas.find_one({"_id": resultado.inserted_id})
    return cita_creada


@app.get(
    "/citas/{id}",
    response_model=Cita,
    status_code=status.HTTP_200_OK,
    tags=["Citas"],
    summary="Buscar cita por ObjectId",
)
async def get_cita_por_id(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectId valido de MongoDB.",
        )

    cita = await coleccion_citas.find_one({"_id": ObjectId(id)})
    if cita:
        return cita

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"La cita con ID '{id}' no fue encontrada en la base de datos.",
    )


@app.put(
    "/citas/{id}",
    response_model=Cita,
    status_code=status.HTTP_200_OK,
    tags=["Citas"],
    summary="Actualizar estado o campos de una cita",
)
async def update_citas(id: str, cita_update: CitaUpdate):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID'{id}' no es un ObjectId valido.",
        )

    datos_a_actualizar = cita_update.model_dump(exclude_unset=True)

    if len(datos_a_actualizar) >= 1:
        resultado_actualizacion = await coleccion_citas.update_one(
            {"_id": ObjectId(id)}, {"$set": datos_a_actualizar}
        )

        if (
            resultado_actualizacion.modified_count == 1
            or resultado_actualizacion.matched_count == 1
        ):
            cita_modificada = await coleccion_citas.find_one({"_id": ObjectId(id)})
            return cita_modificada

    cita_existente = await coleccion_citas.find_one({"_id": ObjectId(id)})
    if cita_existente:
        return cita_existente

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible actualizar. La cita con ID '{id}' no existe.",
    )


@app.delete(
    "/citas/{id}",
    status_code=status.HTTP_200_OK,
    tags=["Citas"],
    summary="Eliminar cita de MongoDB",
)
async def delete_cita(id: str):
    if not ObjectId.is_valid(id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El formato del ID '{id}' no es un ObjectID valido.",
        )

    resultado_eliminacion = await coleccion_citas.delete_one({"_id": ObjectId(id)})

    if resultado_eliminacion.deleted_count == 1:
        return {"mensaje": f"Cita con ID '{id}' eliminada exitosamente de MongoDB."}

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"No es posible eliminar.La cita con ID '{id}' no existe en la base de datos.",
    )
