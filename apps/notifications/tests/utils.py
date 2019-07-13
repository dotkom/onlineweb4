import base64
import os

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


class NotificationTestMixin:
    """
    This was lifted from the pywebpush tests.
    """

    # This is a exported DER formatted string of an ECDH public key
    vapid_key = (
        "MHcCAQEEIPeN1iAipHbt8+/KZ2NIF8NeN24jqAmnMLFZEMocY8RboAoGCCqGSM49"
        "AwEHoUQDQgAEEJwJZq/GN8jJbo1GGpyU70hmP2hbWAUpQFKDByKB81yldJ9GTklB"
        "M5xqEwuPM7VuQcyiLDhvovthPIXx+gsQRQ=="
    )

    def _gen_subscription_info(self,
                               recv_key=None,
                               endpoint="https://example.com/"):
        if not recv_key:
            recv_key = ec.generate_private_key(ec.SECP256R1, default_backend())
        return {
            "endpoint": endpoint,
            "keys": {
                'auth': base64.urlsafe_b64encode(os.urandom(16)).strip(b'='),
                'p256dh': self._get_pubkey_str(recv_key),
            }
        }

    def _get_pubkey_str(self, priv_key):
        return base64.urlsafe_b64encode(
            priv_key.public_key().public_bytes(
                encoding=serialization.Encoding.X962,
                format=serialization.PublicFormat.UncompressedPoint
            )).strip(b'=')
