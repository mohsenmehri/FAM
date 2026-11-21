"""One-time lab TLS certificate generator; runs inside the app image.

Creates a self-signed certificate for the FAM lab gateway.  The private key
never leaves the lab directory and is never part of any release archive.
"""
from __future__ import annotations

import argparse
import datetime
import ipaddress
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, help="directory for fam.crt / fam.key")
    parser.add_argument("--host", default="fam-lab", help="DNS name for the gateway")
    parser.add_argument("--origin", default="", help="browser host or IP to include (SAN)")
    args = parser.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, args.host),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "FAM Lab"),
    ])

    san: list[x509.GeneralName] = [
        x509.DNSName(args.host),
        x509.DNSName("localhost"),
        x509.IPAddress(ipaddress.ip_address("127.0.0.1")),
    ]
    if args.origin:
        try:
            san.append(x509.IPAddress(ipaddress.ip_address(args.origin)))
        except ValueError:
            san.append(x509.DNSName(args.origin))

    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5))
        .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=825))
        .add_extension(x509.SubjectAlternativeName(san), critical=False)
        .sign(key, hashes.SHA256())
    )

    (out / "fam.key").write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
    )
    (out / "fam.crt").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    (out / "fam.key").chmod(0o600)
    print(f"certificate written to {out}/fam.crt (self-signed, lab only)")


if __name__ == "__main__":
    main()
