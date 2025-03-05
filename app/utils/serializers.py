from bson import ObjectId


class Serializers:
    @staticmethod
    async def convert_id_to_string(document):
        """
        Convert MongoDB ObjectId to string for a single document and rename _id to id.
        :param document: A single MongoDB document (dict)
        :return: Document with string id
        """
        try:
            if document and "_id" in document and isinstance(document["_id"], ObjectId):
                document["id"] = str(document.pop("_id"))
            return document
        except Exception as e:
            raise Exception(
                f"Error occurred while converting ObjectId to string: {str(e)}"
            )

    @staticmethod
    async def convert_ids_to_strings(documents):
        """
        Convert MongoDB ObjectIds to strings in a list of
        documents and rename _id to id.
        :param documents: List of MongoDB documents (dicts)
        :return: List of documents with string id
        """
        try:
            return [
                await Serializers.convert_id_to_string(document)
                for document in documents
            ]
        except Exception as e:
            raise Exception(
                f"Error occurred while converting ObjectIds to strings: {str(e)}"
            )
