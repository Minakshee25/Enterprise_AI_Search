from pymilvus import MilvusClient

from app.config import settings


milvus_client = MilvusClient(
    uri=settings.milvus_uri
)