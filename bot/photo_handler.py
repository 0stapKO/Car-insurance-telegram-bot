import os
import requests
from mindee import product
from bot.config import mindee_client

# Handle passport photo using Mindee API
async def handle_passport(file_path, update):
    input_doc = mindee_client.source_from_path(file_path)
    result = mindee_client.parse(product.PassportV1, input_doc)
    prediction = result.document.inference.prediction
    os.remove(file_path)
    first_name = ' '.join([name.value for name in prediction.given_names])
    last_name = prediction.surname.value
    id = prediction.id_number.value
    if not first_name or not last_name or not id:
        raise ValueError('Couldn\'t recognize data from photo.')
    return {
        'First name': first_name,
        'Last name': last_name,
        'ID': id
    }

# Handle vehicle plate photo using Plate Recognizer API
async def handle_plate(file_path, update):
    with open(file_path, 'rb') as f:
        response = requests.post(
            'https://api.platerecognizer.com/v1/plate-reader/',
            files=dict(upload=f),
            headers={'Authorization': 'Token ' + os.getenv('PLATE_RECOGNIZER_TOKEN')}
        )
    os.remove(file_path)
    plate = response.json()['results']
    if not plate:
        raise ValueError('Couldn\'t recognize data from photo.')
    return {'Vehicle plate number': plate[0]['plate'].upper()}