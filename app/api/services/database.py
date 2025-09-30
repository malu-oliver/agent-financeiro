from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import settings
import re


class MongoDB:
    client: AsyncIOMotorClient = None
    database = None


mongodb = MongoDB()


async def connect_to_mongo():
    """Conecta ao MongoDB Atlas usando as configurações do ambiente"""
    try:
        # Conectar ao cluster
        mongodb.client = AsyncIOMotorClient(settings.mongodb_connection_url)

        # Usa o database configurado via .env (DATABASE_NAME)
        mongodb.database = mongodb.client.get_database(settings.mongo_db_name)

        # Testar a conexão
        await mongodb.client.admin.command('ping')
        print("✅ Conectado ao MongoDB Atlas com sucesso!")
        print(f"📊 Cluster: cluster-educa-fin")
        print(f"🏢 Database: {settings.mongo_db_name}")
        return True

    except Exception as e:
        msg = str(e)
        print(f"❌ Erro ao conectar ao MongoDB Atlas: {msg}")

        # Diagnóstico guiado
        hints = []
        if 'bad auth' in msg.lower() or 'Authentication failed'.lower() in msg.lower():
            hints.append(
                "Verifique em MongoDB Atlas > Database Access se existe um *Database User* com o mesmo e-mail e senha (não basta estar em Project Access).")
            hints.append(
                "Se você só tem usuário de 'Project/Organization', crie um Database User: Add New Database User -> Password -> Role: readWriteAnyDatabase ou específica.")
            if '%40' in settings.mongodb_connection_url:
                hints.append(
                    "Encoding OK (%40). Não remova o '@' manualmente.")
            hints.append(
                "Evite caracteres especiais não escapados. A senha atual contém '@' que está corretamente codificado como %40.")
        if 'timeout' in msg.lower():
            hints.append(
                "Verifique Network Access: adicione 0.0.0.0/0 temporariamente para teste.")
        if not hints:
            hints.append(
                "Verifique também: Network Access (IP liberado), se o cluster não está pausado e se a string foi copiada de Drivers.")

        print("🩺 Sugestões de diagnóstico:")
        for i, h in enumerate(hints, 1):
            print(f"   {i}. {h}")

        print("⚠️  API continuará funcionando em modo simulação (sem persistência)")
        mongodb.client = None
        mongodb.database = None
        return False


async def close_mongo_connection():
    """Fecha a conexão com o MongoDB Atlas"""
    if mongodb.client:
        mongodb.client.close()
        print("🔌 Conexão com MongoDB Atlas fechada com sucesso!")


# CRUD Operations
async def create_document(collection_name: str, document: dict):
    """Insere um novo documento em uma coleção."""
    if mongodb.database is None:
        # Modo simulação - retorna ID fake
        import uuid
        print(f"🔄 SIMULAÇÃO: Documento criado em {collection_name}")
        return str(uuid.uuid4())

    collection = mongodb.database[collection_name]
    result = await collection.insert_one(document)
    return str(result.inserted_id)


async def find_document(collection_name: str, query: dict):
    """Busca um documento em uma coleção."""
    if mongodb.database is None:
        # Modo simulação - retorna None
        print(f"🔄 SIMULAÇÃO: Buscando documento em {collection_name}")
        return None

    collection = mongodb.database[collection_name]
    document = await collection.find_one(query)
    return document


async def update_document(collection_name: str, query: dict, new_values: dict):
    """Atualiza um documento em uma coleção."""
    if mongodb.database is None:
        # Modo simulação - retorna 1
        print(f"🔄 SIMULAÇÃO: Documento atualizado em {collection_name}")
        return 1

    collection = mongodb.database[collection_name]
    result = await collection.update_one(query, {"$set": new_values})
    return result.modified_count


async def delete_document(collection_name: str, query: dict):
    """Deleta um documento de uma coleção."""
    if mongodb.database is None:
        # Modo simulação - retorna 1
        print(f"🔄 SIMULAÇÃO: Documento deletado em {collection_name}")
        return 1

    collection = mongodb.database[collection_name]
    result = await collection.delete_one(query)
    return result.deleted_count


async def find_all_documents(collection_name: str, query: dict = None):
    """Busca todos os documentos em uma coleção que correspondem a uma query."""
    if mongodb.database is None:
        # Modo simulação - retorna lista vazia
        print(f"🔄 SIMULAÇÃO: Buscando todos documentos em {collection_name}")
        return []

    collection = mongodb.database[collection_name]
    documents = []
    async for document in collection.find(query or {}):
        documents.append(document)
    return documents


async def ping_database() -> bool:
    """Retorna True se a conexão com o MongoDB estiver ativa e respondendo ao ping."""
    if not mongodb.client:
        return False
    try:
        await mongodb.client.admin.command('ping')
        return True
    except Exception as e:
        print(f"⚠️ Falha no ping do MongoDB: {e}")
        return False
