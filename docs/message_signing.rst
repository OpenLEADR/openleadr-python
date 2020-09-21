.. _message_signing:

===============
Message Signing
===============

OpenADR messages should ideally be signed using an X509 certificate keypair. This allows both parties to verify that the message came from the correct party, and that it was not tampered with in transport. It does not provide message encryption; for that, a transport-level encryption (TLS) should be used.

Overview
--------

The high level overview is this:

1. The VTN creates an X509 certificate and an associated private key. It shares a fingerprint of the certificate with the VEN it connects to (this fingerprint will be printed to your console on startup).
2. The VEN receives a signed (not encrypted) message from the VTN. Each message to the VEN includes the complete X509 Certificate that can be used to verify the signature. The VEN verifies that the message signature is correct, and it verifies that the certificate fingerprint matches the fingerprint that it received from the VEN.

The same process applies with the parties reversed.

For a VEN (client), which talks to one VTN, you simply provide the path to the signing certificate and private key, and the private key passphrase and the VTN's fingerprint on initialization. See: :ref:`client_signing_messages` and :ref:`client_validating_messages`.

For a VTN (server), which talks to multiple VENs, you provide the signing certificate, private key, private key passphrase and a handler function that can look up the certificate fingerprint when given a ven_id. See: :ref:`server_signing_messages`.


Generating certificates
-----------------------

To generate a certificate + private key pair, you can use the following command on Linux:

.. code-block:: text

    openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

This will generate two files (key.pem and cert.pem) and require you to input a passphrase that encrypts/decrypts the private key.

You can provide paths to these files, as well as the passphrase, in your Client or Server initialization. See the examples referred to above.


Replay Protection
-----------------

To prevent an attacker from simple re-playing a previous message (for instance, an Event), unmodified, each signed message contains a ReplayProtect property. This contains a random string (nonce) and a timestamp. Upon validation of the message, it is verified that the timestamp is not older then some preconfigured value (default: 5 seconds), and that the random string has not already been seen during that time window. A cache of the nonces is kept automatically to verify this.

OpenLEADR automatically generates and validates these portions of the signature. Signed messages that do not contain a ReplayProtect element are rejected, as required by the OpenADR specification.

