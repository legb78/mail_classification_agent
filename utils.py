import base64

def decode_base64(data):
    if not data:
        return ""
    decoded = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    return decoded
