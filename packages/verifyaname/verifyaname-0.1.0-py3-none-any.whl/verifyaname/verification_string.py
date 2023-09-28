import base64
import hashlib
import json
from dataclasses import dataclass

from cosmpy.aerial.wallet import Wallet
from cosmpy.crypto.address import Address
from cosmpy.crypto.keypairs import PublicKey
from verifyaname.helpers import encode_length_prefixed

TXT_VERIFICATION_KEY = "fetch-ans-token"
CHAIN_ID = "verification"


def _generate_digest(domain: str, address: str) -> bytes:
    hasher = hashlib.sha256()
    hasher.update(encode_length_prefixed(domain))
    hasher.update(encode_length_prefixed(address))
    return hasher.digest()


def generate_verification_string(wallet: Wallet, domain: str, address: str) -> str:
    signer = wallet.signer()
    signing_data = generate_signing_data(domain, address)

    signature = signer.sign(
        signing_data,
        deterministic=False,
        canonicalise=True,
    )

    return VerificationData(
        pubkey=wallet.public_key().public_key_bytes, signature=signature
    ).encode()


def pk_to_address(pk_bytes: bytes) -> str:
    return str(Address(PublicKey(pk_bytes), "fetch"))


def _signing_data_amino(
    from_address: str,
    data: bytes,
    chain_id: str = CHAIN_ID,
    account_number: int = 0,
    sequence: int = 0,
    memo: str = "",
):
    sign_doc_dict = {
        "account_number": str(account_number),
        "chain_id": str(chain_id),
        "fee": {"amount": [], "gas": "200000"},
        "memo": memo,
        "msgs": [
            {
                "type": "cosmos-sdk/MsgSignData",
                "value": {
                    "data": base64.b64encode(data).decode(),
                    "from_address": from_address,
                },
            }
        ],
        "sequence": str(sequence),
    }

    # Return normalized json string with sorted keys and no whitespace characters in binary format
    return json.dumps(
        sign_doc_dict, sort_keys=True, separators=(",", ":"), indent=None
    ).encode("utf-8")


def generate_signing_data(
    domain: str,
    address: str,
):
    digest = _generate_digest(domain, address)
    signing_data = _signing_data_amino(address, digest)

    return signing_data


@dataclass
class VerificationData:
    pubkey: bytes
    signature: bytes

    @staticmethod
    def _safe_base64_encode(data: bytes):
        """
        Removes any `=` used as padding from the encoded string.
        """
        encoded = base64.urlsafe_b64encode(data).decode()
        return encoded.rstrip("=")

    @staticmethod
    def _safe_base64_decode(data: str):
        """
        Adds back in the required padding before decoding.
        """
        padding = 4 - (len(data) % 4)
        string = data + ("=" * padding)
        return base64.urlsafe_b64decode(string)

    @staticmethod
    def decode(verification_string: str) -> "VerificationData":
        decoded_verification = VerificationData._safe_base64_decode(verification_string)
        pk_bytes = decoded_verification[:33]
        signature = decoded_verification[33:]
        return VerificationData(pk_bytes, signature)

    def encode(self) -> str:
        return VerificationData._safe_base64_encode(self.pubkey + self.signature)


def verify_domain_string(
    data: VerificationData,
    domain: str,
    address: str,
) -> bool:
    # Verify the signature
    signing_data = generate_signing_data(domain, address)

    is_verified = PublicKey(data.pubkey).verify(signing_data, data.signature)

    return is_verified
