def insert_document(collection, data):
    result = collection.insert_one(data)
    return result.inserted_id


def find_document(collection, query):
    result = collection.find(query)
    return list(result)


def update_document(collection, query, new_data):
    result = collection.update_many(query, {"$set": new_data})
    return result.modified_count


def delete_document(collection, query):
    result = collection.delete_many(query)
    return result.deleted_count
