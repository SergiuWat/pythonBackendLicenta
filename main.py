from uuid import uuid4
from opensearchpy import OpenSearch
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to your Angular application's URL
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)

elasticPassword = "AWbtmGda2Q7BI2bYpdjyF4qd"
elasticUser = "elastic"
elasticAPIKey = "XYjEEt6fTnKsXEfTro4Kxg"
elasticURL = "https://8f9677360fc34e2eb943d737b2597c7b.us-east-1.aws.found.io"
opensearch_index = "sensors_and_coordinates"
tempId = str(uuid4())

host = 'localhost'  # or the IP address/domain of your OpenSearch cluster
port = 9200  # default OpenSearch port
auth = (elasticUser, elasticPassword)  # Your cluster credentials
opensearch_client = OpenSearch(
    hosts=[elasticURL],
    http_auth=auth,
    use_ssl=True,  # Set to True if your cluster is behind HTTPS
    verify_certs=True)

class SensorData(BaseModel):
    temperature: float
    pressure: float
    humidity: float
    gas: float
    altitude: float
    latitude: float
    longitude: float
    date: str


@app.get("/get-all-data/")
async def get_all_data():
    try:
        search_response = opensearch_client.search(index=opensearch_index, body={"query": {"match_all": {}}})
        documents = search_response["hits"]["hits"]

        # Extract sensor data fields from each document
        extracted_data = []
        for doc in documents:
            source = doc["_source"]
            extracted_data.append({
                "temperature": source["temperature"],
                "pressure": source["pressure"],
                "humidity": source["humidity"],
                "gas": source["gas"],
                "altitude": source["altitude"],
                "latitude": source["latitude"],
                "longitude": source["longitude"],
                "date": source["date"]

            })
    except Exception as e:
        print("An error occurred while retrieving documents:", str(e))
        return []
    return extracted_data

@app.delete("/delete-all-data/")
async def delete_all_data():
    try:
        opensearch_client.delete_by_query(index=opensearch_index, body={"query": {"match_all": {}}})
        print("All documents deleted from index:", opensearch_index)
    except Exception as e:
        print("An error occurred while deleting documents:", str(e))
    return {"message": "All data deleted successfully from index: " + opensearch_index}

@app.post("/add-data/")
async def create_sensor_data(sensor_data: SensorData):
    # Create a unique ID for the document
    document_id = str(uuid4())
    current_datatime = datetime.now()
    formatted_date = current_datatime.strftime("%d/%m/%Y %H:/%M")
    sensor_data.date = formatted_date
    # Initialize OpenSearch client
    opensearch_client = OpenSearch(
        hosts=[elasticURL],
        http_auth=(elasticUser, elasticPassword),
        use_ssl=True,
        verify_certs=True
    )

    # Index the sensor data
    index_response = opensearch_client.index(
        index=opensearch_index,
        body=sensor_data.dict(),
        id=document_id
    )
    return {"message": "Sensor data indexed successfully", "document_id": document_id}