import binascii
import json
import base64
from usepy import useAdDict


def decode_payload(payload):
    try:
        decoded_payload = base64.urlsafe_b64decode(payload + '=').decode()
        data = json.loads(decoded_payload)
        return useAdDict(data)
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError) as e:
        print(f"Error decoding payload: {e}")
        return None
