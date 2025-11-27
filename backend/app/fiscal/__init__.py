"""Pacote dedicado aos fluxos fiscais.

Esta camada simula as integrações reais com a SEFAZ, mantendo a mesma
interface pública que será utilizada quando o conector oficial estiver
pronto.
"""

from .contingency import ContingencyManager
from .nfce import NfceProcessor
from .sefaz import SefazClient
from .signature import DigitalSigner, SignedXml
from .tax_tables import TaxTableRepository
from .xml_builder import NfceXmlBuilder

__all__ = [
    "ContingencyManager",
    "DigitalSigner",
    "NfceProcessor",
    "SefazClient",
    "SignedXml",
    "TaxTableRepository",
    "NfceXmlBuilder",
]
