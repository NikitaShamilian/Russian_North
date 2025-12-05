from qdrant_client import QdrantClient

qdrant_client = QdrantClient(
    url="https://63c4a6fa-847f-49ce-801a-b3edebdaefa2.europe-west3-0.gcp.cloud.qdrant.io:6333", 
    api_key="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2Nlc3MiOiJtIn0.zk7ObI9pXmTfjg6riNrlrWekNP2_OoXuKbs1mEvQxOE",
)

print(qdrant_client.get_collections())