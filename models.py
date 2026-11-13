from datetime import datetime
from typing import Annotated, Optional

from bson import ObjectId
from pydantic import BaseModel, ConfigDict, Field
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


class _ObjectIdPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        def validate(v):
            if isinstance(v, ObjectId):
                return str(v)
            if isinstance(v, str) and ObjectId.is_valid(v):
                return v
            raise ValueError("Id invalido de MongoDB (ObjectId")

        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.no_info_plain_validator_function(validate),
            serialization=core_schema.to_string_ser_schema(),
        )


PyObjectId = Annotated[str, _ObjectIdPydanticAnnotation]


class CitaEstetica(BaseModel):
    cliente: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Ingrese nombre del Cliente",
        examples=["Example: Juan Perez"],
    )
    servicio_solicitado: str = Field(
        ...,
        max_length=500,
        description="Ingrese servicio solicitado por el cliente.",
        examples=["Example: Lavado de Cabello"],
    )
    duracion_minutos: int = Field(
        ...,
        ge=1,
        le=99999,
        description="Titulo descriptivo de la tarea",
    )
    confirmada: bool = Field(
        default=False,
        description="El cliente confirmo el servicio",
    )


class CitaCreate(CitaEstetica):
    pass


class CitaUpdate(BaseModel):
    cliente: Optional[str] = Field(None, min_length=3, max_length=50)
    servicio_solicitado: Optional[str] = Field(None, max_length=500)
    duracion_minutos: Optional[int] = Field(None, ge=1, le=9999)
    confirmada: Optional[bool] = None


class Cita(CitaEstetica):
    id: PyObjectId = Field(
        alias="_id", description="Identificador unico ObjectId de MongoDB"
    )
    fecha_creacion: datetime = Field(
        default_factory=datetime.now, description="Fecha de registro"
    )

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "_id": "1234567890abcdef09876543",
                "cliente": "Juan Rodriguez",
                "servicio_solicitado": "Servicio de Spa",
                "duracion_minutos": 30,
                "confirmada": False,
                "fecha_creacion": "2026-11-05T18:30:00",
            }
        },
    )
