from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha1


@dataclass
class SignedXml:
    xml: str
    certificate_serial: str


class DigitalSigner:
    """Simula assinatura digital com certificado A1."""

    def __init__(self, certificate_serial: str = "DEMO123456") -> None:
        self.certificate_serial = certificate_serial

    def sign(self, xml: str) -> SignedXml:
        # Simula assinatura adicionando um hash ao final do XML.
        signature = sha1(xml.encode()).hexdigest()
        signed_xml = f"{xml}\n<!-- signed:{signature} -->"
        return SignedXml(xml=signed_xml, certificate_serial=self.certificate_serial)
