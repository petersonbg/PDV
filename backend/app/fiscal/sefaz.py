from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4


@dataclass
class SefazResponse:
    success: bool
    message: str
    protocol: str | None
    access_key: str | None
    processed_at: datetime


class SefazClient:
    """Cliente fake para envio e cancelamento na SEFAZ."""

    def send_signed_xml(self, signed_xml: str) -> SefazResponse:
        protocol = str(uuid4())[:8]
        access_key = f"{datetime.utcnow():%y%m}{protocol}"
        message = "XML recebido e processado (mock)."
        return SefazResponse(
            success=True,
            message=message,
            protocol=protocol,
            access_key=access_key,
            processed_at=datetime.utcnow(),
        )

    def cancel(self, access_key: str, justification: str) -> SefazResponse:
        message = f"Cancelamento registrado (mock) para {access_key}: {justification}"
        return SefazResponse(
            success=True,
            message=message,
            protocol=str(uuid4())[:8],
            access_key=access_key,
            processed_at=datetime.utcnow(),
        )

    def status(self, access_key: str) -> SefazResponse:
        message = "Documento autorizado (mock)."
        return SefazResponse(
            success=True,
            message=message,
            protocol=str(uuid4())[:8],
            access_key=access_key,
            processed_at=datetime.utcnow(),
        )
