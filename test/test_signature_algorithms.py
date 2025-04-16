import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa, dsa, ec, ed25519, ed448
from openleadr.messaging import get_signature_algorithm_from_private_key


test_keys = {
    "rsa": rsa.generate_private_key(public_exponent=65537, key_size=2048),
    "dsa": dsa.generate_private_key(key_size=2048),
    "ec": ec.generate_private_key(ec.SECP256R1()),
    "ed25519": ed25519.Ed25519PrivateKey.generate(),
    "ed448": ed448.Ed448PrivateKey.generate()
}


@pytest.mark.parametrize("key_type, expected_alg", [
    ("rsa", "rsa-sha256"),
    ("dsa", "dsa-sha256"),
    ("ec", "ecdsa-sha256"),
    ("ed25519", "rsa-sha256"),
    ("ed448", "rsa-sha256"),
])
def test_key_type_sign_alg_match(key_type, expected_alg):
    test_key = test_keys[key_type]
    key_encoding = serialization.Encoding.PEM
    key_format = serialization.PrivateFormat.PKCS8
    key_encryption_alg = serialization.NoEncryption()
    key_bytes = test_key.private_bytes(key_encoding, key_format, key_encryption_alg)

    detected_alg = get_signature_algorithm_from_private_key(key_bytes)

    assert detected_alg == expected_alg
