from app.database.connection import mongodb

async def create_document(collection_name: str, document: dict):
    """Insere um novo documento em uma coleção."""
    collection = mongodb.database[collection_name]
    result = await collection.insert_one(document)
    return str(result.inserted_id)

async def find_document(collection_name: str, query: dict):
    """Busca um documento em uma coleção."""
    collection = mongodb.database[collection_name]
    document = await collection.find_one(query)
    return document

async def update_document(collection_name: str, query: dict, new_values: dict):
    """Atualiza um documento em uma coleção."""
    collection = mongodb.database[collection_name]
    result = await collection.update_one(query, {"$set": new_values})
    return result.modified_count

async def delete_document(collection_name: str, query: dict):
    """Deleta um documento de uma coleção."""
    collection = mongodb.database[collection_name]
    result = await collection.delete_one(query)
    return result.deleted_count

async def find_all_documents(collection_name: str, query: dict = None):
    """Busca todos os documentos em uma coleção que correspondem a uma query."""
    collection = mongodb.database[collection_name]
    documents = []
    async for document in collection.find(query or {}):
        documents.append(document)
    return documents

