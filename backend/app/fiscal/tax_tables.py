from __future__ import annotations

from dataclasses import dataclass


@dataclass
class TaxEntry:
    code: str
    description: str


class TaxTableRepository:
    """Mocka tabelas tributárias necessárias para NFC-e."""

    def __init__(self) -> None:
        self.ncm = {
            "6109": "Camisetas de malha",
            "2203": "Cervejas de malte",
        }
        self.cfop = {
            "5102": "Venda de mercadoria adquirida de terceiros",
            "5101": "Venda de produção do estabelecimento",
        }
        self.cst = {
            "00": "Tributada integralmente",
            "20": "Com redução de base de cálculo",
        }
        self.csosn = {
            "102": "Tributada pelo Simples Nacional sem permissão de crédito",
            "900": "Outros",
        }

    def find_ncm(self, code: str) -> TaxEntry | None:
        description = self.ncm.get(code)
        return TaxEntry(code, description) if description else None

    def find_cfop(self, code: str) -> TaxEntry | None:
        description = self.cfop.get(code)
        return TaxEntry(code, description) if description else None

    def find_cst(self, code: str) -> TaxEntry | None:
        description = self.cst.get(code)
        return TaxEntry(code, description) if description else None

    def find_csosn(self, code: str) -> TaxEntry | None:
        description = self.csosn.get(code)
        return TaxEntry(code, description) if description else None
