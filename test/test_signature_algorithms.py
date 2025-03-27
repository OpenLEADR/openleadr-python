import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec, ed25519, ed448
from openleadr.messaging import get_signature_algorithm_from_private_key


@pytest.mark.parametrize("key, expected_alg", [
    (rsa.generate_private_key(public_exponent=65537, key_size=2048), "rsa-sha256"),
    (dsa.generate_private_key(key_size=2048), "dsa-sha256"),
    (ec.generate_private_key(ec.SECP256R1()), "ecdsa-sha3-256"),
    (ed25519.Ed25519PrivateKey.generate(), "rsa-sha256"),
    (ed448.Ed448PrivateKey.generate(), "rsa-sha256"),
])
def test_key_type_sign_alg_match(key, expected_alg):
    key_encoding = serialization.Encoding.PEM
    key_format = serialization.PrivateFormat.PKCS8
    key_encryption_alg = serialization.NoEncryption()
    key_bytes = key.private_bytes(key_encoding, key_format, key_encryption_alg)
    detected_alg = get_signature_algorithm_from_private_key(key_bytes)

    assert detected_alg == expected_alg, f"Expected {expected_alg} but got {detected_alg}"