from __future__ import annotations

from datetime import datetime

from app.fiscal.tax_tables import TaxTableRepository
from app.schemas.fiscal import InvoiceItem


class NfceXmlBuilder:
    """Constrói uma estrutura XML simplificada da NFC-e."""

    def __init__(self, tax_tables: TaxTableRepository) -> None:
        self.tax_tables = tax_tables

    def build(self, sale_id: int, items: list[InvoiceItem]) -> str:
        issued_at = datetime.utcnow().isoformat()
        xml_lines = ["<NFe>", "  <infNFe>", f"    <ide><cNF>{sale_id}</cNF><dhEmi>{issued_at}</dhEmi></ide>"]

        for index, item in enumerate(items, start=1):
            ncm = self.tax_tables.find_ncm(item.ncm)
            cfop = self.tax_tables.find_cfop(item.cfop)
            cst = self.tax_tables.find_cst(item.cst)
            csosn = self.tax_tables.find_csosn(item.csosn) if item.csosn else None
            xml_lines.append("    <det>")
            xml_lines.append(f"      <prod><cProd>{item.product_code}</cProd><xProd>{item.description}</xProd></prod>")
            xml_lines.append(
                f"      <imposto><ICMS><orig>0</orig><CST>{item.cst}</CST><CFOP>{item.cfop}</CFOP>"
                f"<NCM>{item.ncm}</NCM></ICMS></imposto>"
            )
            xml_lines.append(
                f"      <!-- tributações: NCM={ncm.description if ncm else 'desconhecido'}, "
                f"CFOP={cfop.description if cfop else 'desconhecido'}, "
                f"CST={cst.description if cst else 'desconhecido'}, "
                f"CSOSN={csosn.description if csosn else 'n/a'} -->"
            )
            xml_lines.append(
                f"      <infAdProd>item {index} - qtd {item.quantity} x {item.unit_price}</infAdProd>"
            )
            xml_lines.append("    </det>")

        xml_lines.extend(["  </infNFe>", "</NFe>"])
        return "\n".join(xml_lines)
