from pydantic import BaseModel, Field


class PrinterConfig(BaseModel):
    host: str = Field(..., description="Endereço IP ou hostname da impressora")
    port: int = Field(9100, description="Porta de rede para comunicação ESC/POS")
    timeout: int = Field(10, description="Tempo de espera da conexão, em segundos")
    encoding: str = Field(
        "CP860_PORTUGUESE",
        description="Tabela de caracteres (code page) utilizada pela impressora",
    )


class PrintSaleRequest(BaseModel):
    sale_id: int = Field(..., description="Identificador da venda a ser impressa")
    printer: PrinterConfig


class PrintJobResult(BaseModel):
    status: str
    message: str
    sale_id: int
    printer: PrinterConfig
    receipt_preview: str
