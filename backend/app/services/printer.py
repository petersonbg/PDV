from datetime import datetime

from escpos.printer import Network

from app.models.sale import Sale


class ThermalPrinterService:
    """Serviço responsável por dialogar com impressoras térmicas ESC/POS."""

    def __init__(
        self,
        host: str,
        port: int = 9100,
        timeout: int = 10,
        encoding: str = "CP860_PORTUGUESE",
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.encoding = encoding

    def _connect(self) -> Network:
        printer = Network(self.host, port=self.port, timeout=self.timeout)
        if self.encoding:
            try:
                printer.charcode(self.encoding)
            except ValueError:
                # Mantém o padrão da impressora caso o code page não seja suportado
                pass
        return printer

    @staticmethod
    def _format_line(label: str, value: str, width: int = 32) -> str:
        clean_label = label[: width - len(value) - 1]
        return f"{clean_label}{'.' * (width - len(clean_label) - len(value))}{value}\n"

    def _format_sale_receipt(self, sale: Sale) -> str:
        lines: list[str] = []
        lines.append("PDV - COMPROVANTE DE VENDA")
        lines.append(datetime.utcnow().strftime("%d/%m/%Y %H:%M UTC"))
        lines.append(f"CÓDIGO: {sale.code}")
        lines.append("-" * 32)

        for item in sale.items:
            name = item.product.name if item.product else "Produto"
            lines.append(name[:32])
            lines.append(
                f" x{float(item.quantity):.3f} @ {float(item.unit_price):.2f}"
                f" = {float(item.total_price):.2f}"
            )
            lines.append("-" * 32)

        subtotal = sum(float(item.total_price) for item in sale.items)
        lines.append(self._format_line("Subtotal", f"{subtotal:.2f}"))
        if float(sale.discount or 0) > 0:
            lines.append(self._format_line("Desconto", f"-{float(sale.discount):.2f}"))
        lines.append(self._format_line("Total", f"{float(sale.total):.2f}"))

        if sale.payments:
            lines.append("Pagamentos:")
            for payment in sale.payments:
                status = "pago" if payment.paid else "pendente"
                lines.append(
                    f"- {payment.method}: {float(payment.amount):.2f} ({status})"
                )

        lines.append("Obrigado pela preferência!")
        return "\n".join(lines)

    def print_sale(self, sale: Sale) -> str:
        """Gera e envia o comprovante de venda para a impressora."""

        receipt = self._format_sale_receipt(sale)
        printer = self._connect()
        printer.set(align="center", text_type="B", width=1, height=1)
        printer.text(f"{receipt}\n\n")
        printer.cut()
        printer.close()
        return receipt
