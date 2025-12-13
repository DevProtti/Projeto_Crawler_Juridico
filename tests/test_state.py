import pytest
from pydantic import ValidationError
from src.graph.state import DocumentObj

def test_document_obj_validacao_sucesso():
    """Testa se consigo criar um documento com dados corretos."""
    doc = DocumentObj(
        title="Notícia Teste",
        content="Conteúdo do teste",
        url="http://teste.com",
        source="Fonte Teste",
        published_at="2024-01-01"
    )
    assert doc.title == "Notícia Teste"
    assert doc.url == "http://teste.com"

def test_document_obj_validacao_erro():
    """Testa se o Pydantic grita quando falta campo obrigatório."""
    # Aqui dizemos: "Eu espero que aconteça um ValidationError dentro deste bloco"
    with pytest.raises(ValidationError):
        # Tentar criar sem URL e sem Source
        DocumentObj(
            title="Notícia Incompleta",
            content="Falta coisa aqui",
            # url="...",  <-- Comentei propositalmente
             published_at="2024-01-01"
        )