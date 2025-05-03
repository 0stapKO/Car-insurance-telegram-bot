import os
import requests
from mindee import product
from config import mindee_client

async def handle_passport(file_path, update):
    input_doc = mindee_client.source_from_path(file_path)
    result = mindee_client.parse(product.PassportV1, input_doc)
    prediction = result.document.inference.prediction
    os.remove(file_path)
    
    return {
        'First name': str([name.value for name in prediction.given_names]).replace('\'', '').replace(',', '')[1:-1],
        'Last name': prediction.surname.value,
        'ID': prediction.id_number.value
    }

async def handle_plate(file_path, update):
    with open(file_path, "rb") as f:
        response = requests.post(
            "https://api.platerecognizer.com/v1/plate-reader/",
            files=dict(upload=f),
            headers={'Authorization': 'Token ' + os.getenv('PLATE_RECOGNIZER_TOKEN')}
        )
    os.remove(file_path)
    return {'Vehicle plate number': response.json()['results'][0]['plate'].upper()}