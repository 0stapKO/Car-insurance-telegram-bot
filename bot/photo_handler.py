import os
import requests
from mindee import product
from bot.config import mindee_client, PLATE_RECOGNIZER_TOKEN

async def parse_photo_data(file_path, context):
    result = {} # Dictiona ryto store extracted data

    try:
        # Try to recognize passport data using Mindee API
        doc = mindee_client.source_from_path(file_path)
        prediction = mindee_client.parse(product.PassportV1, doc).document.inference.prediction

        given_names = [n.value for n in prediction.given_names if n.value]
        surname = prediction.surname.value
        id_number = prediction.id_number.value

        # If any essential field is missing, raise an error 
        if not given_names or not surname or not id_number:
            raise ValueError("Couldn't recognize passport data.")

        result.update({
            'First name': ' '.join(given_names),
            'Last name': surname,
            'ID': id_number
        })

    except Exception as e:
        print(f"Error with passport data recognition: {e}")
        
        # Fall back to license plate recognition
        try:
            with open(file_path, 'rb') as f:
                res = requests.post(
                    'https://api.platerecognizer.com/v1/plate-reader/',
                    files={'upload': f},
                    headers={'Authorization': 'Token ' + PLATE_RECOGNIZER_TOKEN}
                )
                plates = res.json().get('results', [])
                # If plate detected, add it to result
                if plates:
                    result['Vehicle license plate'] = plates[0]['plate'].upper()
        except Exception as e:
            print(f"Error with license plate recognition: {e}")

    finally:
        # Always delete the temporary image file after processing
        os.remove(file_path)

    # If no data was extracted, return an error message
    if not result:
        result['Error'] = 'Could not extract data from image.'

    return result
