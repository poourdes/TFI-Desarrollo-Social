from app.services.contact import decrypt_contact, encrypt_contact

DESCRIPTION_DOMAIN = b"report-description:v1:"


def encrypt_description(value: str) -> bytes:
    return encrypt_contact(value, domain=DESCRIPTION_DOMAIN)


def decrypt_description(token: bytes) -> str:
    return decrypt_contact(token, domain=DESCRIPTION_DOMAIN)
