from decouple import config
from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URL = config("MONGODB_URL", default="mongodb://localhost:27017", cast=str)
DATABASE_NAME = config("DATABASE_NAME", default="spa_db", cast=str)

client = AsyncIOMotorClient(MONGODB_URL)

database = client[DATABASE_NAME]

coleccion_citas = database["citas"]


async def verificar_conexion():
    try:
        await client.admin.command("ping")
        print(f"Conexion exitosa a MongoDB - Base de Datos: '{DATABASE_NAME}'")
    except Exception as e:
        print(f"Error de conexion a MongoDB: {e}")
