from typing import List, Dict, Any


async def convert_objectid(document: Dict[str, Any]) -> Dict[str, Any]:
    if document and "_id" in document:
        document["id"] = str(document["_id"])
        del document["_id"]
    return document


async def convert_objectids_list(
    documents: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    return [await convert_objectid(document) for document in documents]
