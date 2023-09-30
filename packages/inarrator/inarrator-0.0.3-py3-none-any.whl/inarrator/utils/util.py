import base64


def base64url_decode(input_string: str) -> str:
    """Encode a base64url string to string

    Args:
    -----
        input_string: Input String

    Returns:
    --------
        Decoded string

    """
    input_string = input_string.replace("-", "+").replace("_", "/")
    padding = len(input_string) % 4
    if padding:
        input_string += "=" * (4 - padding)
    decoded_bytes = base64.b64decode(input_string)
    decoded_string = decoded_bytes.decode("utf-8")  # Adjust encoding if needed
    return decoded_string
