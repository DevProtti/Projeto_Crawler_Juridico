import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from src.core.discovery import (
    _fetch_single_rss,
    fetch_tavily_search,
    get_all_initial_documents
)

# --- MOCKS DE DADOS --- #
MOCK_RSS_XML = """
<rss version="2.0">
<channel>
    <title>Fonte Teste</title>
    <item>
        <title>Notícia 1</title>
        <link>http://teste.com/1</link>
        <description>Resumo teste</description>
        <pubDate>Fri, 12 Dec 2025 10:00:00 GMT</pubDate>
    </item>
</channel>
</rss>
"""

# --- TESTES --- #

@pytest.mark.asyncio
async def test_fetch_single_rss_sucesso():
    """
    Verifica se _fetch_single_rss faz o parse correto do XML quando a requisição é 200 OK.
    """
    # 1. Configurar o objeto de RESPOSTA (O que acontece DENTRO do async with)
    mock_response = AsyncMock()
    mock_response.status = 200
    mock_response.text.return_value = MOCK_RSS_XML

    # 2. Configurar o CONTEXT MANAGER (O comportamento do async with)
    # session.get() retorna um objeto que tem __aenter__ e __aexit__
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    mock_context.__aexit__.return_value = None

    # 3. Configurar a SESSÃO (O objeto aiohttp.ClientSession)
    mock_session = MagicMock()
    # Quando chamamos session.get(), ele retorna o context manager configurado acima
    mock_session.get.return_value = mock_context

    # Execução
    url = "http://fake-rss.com"
    resultado = await _fetch_single_rss(mock_session, url)

    # Asserções
    assert len(resultado) == 1
    assert resultado[0]["title"] == "Notícia 1"
    assert resultado[0]["type"] == "rss"

@pytest.mark.asyncio
async def test_fetch_single_rss_erro_http():
    """
    Verifica se retorna lista vazia quando status != 200.
    """
    # Configura resposta de erro
    mock_response = AsyncMock()
    mock_response.status = 404 # Not Found
    
    # Configura Context Manager
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    
    # Configura Sessão
    mock_session = MagicMock()
    mock_session.get.return_value = mock_context

    resultado = await _fetch_single_rss(mock_session, "http://fake-rss.com")
    
    assert resultado == []

@pytest.mark.asyncio
async def test_fetch_tavily_search_filtragem_score():
    """
    Verifica se a função filtra corretamente resultados com score < 0.75.
    """
    mock_tavily_response = {
        "results": [
            {
                "title": "Alta Relevância", 
                "url": "http://a.com", 
                "content": "Bom", 
                "score": 0.90,
                "published_date": "2025-01-01"
            },
            {
                "title": "Baixa Relevância", 
                "url": "http://b.com", 
                "content": "Ruim", 
                "score": 0.50, # Deve ser removido
                "published_date": "2025-01-01"
            }
        ]
    }

    # Patch na classe e na API Key
    with patch("src.core.discovery.AsyncTavilyClient") as MockClient, \
         patch("src.core.discovery.TAVILY_API_KEY", "fake-key"):
        
        # O PULO DO GATO: Garantir que .search seja um AsyncMock
        # Sem isso, ele cria um MagicMock normal que falha no 'await'
        instance = MockClient.return_value
        instance.search = AsyncMock(return_value=mock_tavily_response)

        # Executa
        queries = ["query"]
        resultado = await fetch_tavily_search(queries)

        # Asserções
        assert len(resultado) == 1
        assert resultado[0]["title"] == "Alta Relevância"

@pytest.mark.asyncio
async def test_get_all_initial_documents_integracao():
    """
    Verifica se a orquestradora une RSS e Tavily.
    """
    # Mockamos as funções internas para não testar tudo de novo
    with patch("src.core.discovery.fetch_rss_feeds") as mock_rss, \
         patch("src.core.discovery.fetch_tavily_search") as mock_tavily:
        
        # Configura retornos simulados (Futures)
        mock_rss.return_value = [{"title": "RSS", "type": "rss"}]
        mock_tavily.return_value = [{"title": "Tavily", "type": "tavily_search"}]

        # Executa
        resultado = await get_all_initial_documents()

        # Verifica união
        assert len(resultado) == 2
        # Verifica se contém elementos de ambos os tipos
        types = [r["type"] for r in resultado]
        assert "rss" in types
        assert "tavily_search" in types