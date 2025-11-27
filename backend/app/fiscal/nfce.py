from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from app.fiscal.contingency import ContingencyManager
from app.fiscal.sefaz import SefazClient, SefazResponse
from app.fiscal.signature import DigitalSigner
from app.fiscal.tax_tables import TaxTableRepository
from app.fiscal.xml_builder import NfceXmlBuilder
from app.schemas.fiscal import InvoiceItem


@dataclass
class NfceEmissionResult:
    success: bool
    message: str
    protocol: str | None
    access_key: str | None
    contingency: bool
    xml: str


class NfceProcessor:
    def __init__(
        self,
        *,
        tax_tables: TaxTableRepository,
        signer: DigitalSigner,
        sefaz_client: SefazClient,
        contingency_manager: ContingencyManager,
    ) -> None:
        self.tax_tables = tax_tables
        self.signer = signer
        self.sefaz_client = sefaz_client
        self.contingency_manager = contingency_manager
        self.xml_builder = NfceXmlBuilder(tax_tables)

    def emit(self, sale_id: int, items: list[InvoiceItem], offline: bool, contingency_reason: str | None) -> NfceEmissionResult:
        xml = self.xml_builder.build(sale_id, items)
        signed = self.signer.sign(xml)

        if offline:
            reference = f"CONT-{uuid4().hex[:8]}"
            self.contingency_manager.enqueue(reference, signed.xml, contingency_reason)
            return NfceEmissionResult(
                success=True,
                message="Documento emitido em contingência offline.",
                protocol=reference,
                access_key=None,
                contingency=True,
                xml=signed.xml,
            )

        sefaz_response = self.sefaz_client.send_signed_xml(signed.xml)
        return self._map_response(sefaz_response, signed.xml)

    def cancel(self, access_key: str, justification: str) -> NfceEmissionResult:
        sefaz_response = self.sefaz_client.cancel(access_key, justification)
        return self._map_response(sefaz_response, xml="")

    def status(self, access_key: str) -> NfceEmissionResult:
        sefaz_response = self.sefaz_client.status(access_key)
        return self._map_response(sefaz_response, xml="")

    def _map_response(self, response: SefazResponse, xml: str) -> NfceEmissionResult:
        return NfceEmissionResult(
            success=response.success,
            message=response.message,
            protocol=response.protocol,
            access_key=response.access_key,
            contingency=False,
            xml=xml,
        )
