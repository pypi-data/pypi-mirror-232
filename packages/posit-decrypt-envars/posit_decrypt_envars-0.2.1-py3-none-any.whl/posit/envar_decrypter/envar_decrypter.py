"""Posit decryption utility"""
import os
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend


def get_encrypted_env_vars() -> list:
    """Function to load environment variables to decrypt db username and password

    Raises:
        Exception: If environment variables are not present an excepition is raised

    Returns:
        list: db redshift username, db redshift password, db s3 username
        and db s3 password
    """
    if "DB_USERNAME" in os.environ:
        envar_redshift_user = os.environ["DB_USERNAME"]
    else:
        raise Exception("Missing DB_USERNAME environment variable")

    if "DB_PASSWORD" in os.environ:
        envar_redshift_password = os.environ["DB_PASSWORD"]
    else:
        raise Exception("Missing DB_PASSWORD environment variable")

    if "S3_USERNAME" in os.environ:
        envar_s3_user = os.environ["S3_USERNAME"]
    else:
        raise Exception("Missing S3_USERNAME environment variable")

    if "S3_PASSWORD" in os.environ:
        envar_s3_password = os.environ["S3_PASSWORD"]
    else:
        raise Exception("Missing S3_PASSWORD environment variable")

    if "DECRYPTKEY" in os.environ:
        encrypted_decrypt_key = os.environ["DECRYPTKEY"]
    else:
        raise Exception("Missing DECRYPTKEY environment variable")

    private_key = serialization.load_pem_private_key(
        bytes(str(encrypted_decrypt_key.replace("\\n", "\n")), "utf-8"),
        password=None,
        backend=default_backend(),
    )

    encrypted_redshift_user = bytes.fromhex(envar_redshift_user)
    decrypt_redshift_user = private_key.decrypt(
        encrypted_redshift_user,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    encrypted_redshift_pass = bytes.fromhex(envar_redshift_password)
    decrypt_redshift_pass = private_key.decrypt(
        encrypted_redshift_pass,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    encrypted_s3_user = bytes.fromhex(envar_s3_user)
    decrypt_s3_user = private_key.decrypt(
        encrypted_s3_user,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    encrypted_s3_pass = bytes.fromhex(envar_s3_password)
    decrypt_s3_pass = private_key.decrypt(
        encrypted_s3_pass,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    decrypted_vars = [
        decrypt_redshift_user.decode(),
        decrypt_redshift_pass.decode(),
        decrypt_s3_user.decode(),
        decrypt_s3_pass.decode(),
    ]

    return decrypted_vars
