from cash_flow.models import DocumentType  # substitua 'myapp' pelo nome do seu app
from uuid import uuid4

# Lista dos tipos de documentos fornecida por você
document_types_list = [
    "Cartão", "Cartão de Crédito", "Cartão de Débito", "Cheque", "Cheque de Terceiros",
    "Cheque Devolvido", "Cheque Pré", "Cobrança de Concessionária", "Comissão",
    "Contrato", "Convênios", "Crediário", "Crédito em Conta", "CT-e", "Cupom Fiscal",
    "DAE", "DAJE", "DAM", "DAMFE", "DANFSE", "DAR", "DARE", "DARF", "DARJ", "DARM",
    "DAS", "DDA", "Débito Automático", "Débito em Conta", "Depósito", "IPVA",
    "Licenciamento", "Medição", "Multas", "Mútuo", "Nota de Crédito", "Nota de Débito",
    "Nota Fiscal", "Nota Fiscal de Abastecimento", "Nota Fiscal de Consumidor",
    "Nota Fiscal de Devolução", "Nota Fiscal de Serviço", "Nota Fiscal de Telecomunicações",
    "Nota Fiscal Eletrônica", "Outros", "Pensão Alimentícia", "Permuta", "Pro-Labore",
    "Protesto", "Provisão", "Recibo", "Reembolso", "Rescisão Trabalhista", "RPA", "Saque",
    "Tarifa", "Taxa", "TED", "Ticket", "Transferência"
]

# Criando uma lista de objetos DocumentType
document_type_objects = [
    DocumentType(document_type=doc_type, uuid_document_type=uuid4())
    for doc_type in document_types_list
]

# Usando bulk_create para inserir todos os objetos de uma vez
DocumentType.objects.bulk_create(document_type_objects)

from populate_document_type import *