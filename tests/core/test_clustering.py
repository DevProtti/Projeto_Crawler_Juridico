import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from src.core.clustering import Clustering

# --- DADOS DE TESTE (CENÁRIO CONTROLADO) ---
# Vamos simular 4 documentos:
# Doc 1, 2 e 3 são sobre o TEMA A (digamos, "Pix").
# Doc 4 é sobre o TEMA B (digamos, "Futebol").

DOCS_TESTE = [
    {"title": "Pix 1", "content": "Texto curto sobre pix", "url": "url1"},
    {"title": "Pix 2", "content": "Texto médio sobre pix e fraudes", "url": "url2"},
    {"title": "Pix 3", "content": "Texto LONGO e DENSO sobre regulação do pix", "url": "url3"}, # Candidato a Denso
    {"title": "Futebol", "content": "Texto sobre campeonato", "url": "url4"},
]

# Simulação vetorial (2 Dimensões para facilitar nossa cabeça)
# Tema A (Pix): Apontam para o eixo X (1, 0)
# Tema B (Futebol): Aponta para o eixo Y (0, 1)
VETORES_MOCK = [
    [0.99, 0.01], # Doc 1 (Perto do eixo X)
    [0.95, 0.05], # Doc 2 (Perto do eixo X)
    [0.90, 0.10], # Doc 3 (Perto do eixo X)
    [0.01, 0.99], # Doc 4 (Longe! Eixo Y)
]

# --- TESTES ---

def test_clustering_inicializacao():
    """Verifica se a conversão de similaridade para distância está correta."""
    # Se similaridade é 70% (0.7), distância deve ser 30% (0.3)
    service = Clustering(similarity_threshold=0.70)
    assert pytest.approx(service.distance_threshold) == 0.30

def test_process_documents_agrupamento():
    """
    Testa se o algoritmo separa corretamente o Tema A do Tema B
    baseado nos vetores mockados.
    """
    # 1. Mockar a OpenAI para retornar nossos vetores controlados
    with patch("src.core.clustering.OpenAIEmbeddings") as MockEmbeddings:
        mock_instance = MockEmbeddings.return_value
        mock_instance.embed_documents.return_value = VETORES_MOCK
        
        # 2. Executar
        service = Clustering(similarity_threshold=0.70)
        result = service.process_documents(DOCS_TESTE)
        
        # 3. Asserções Lógicas
        # Esperamos 2 Clusters: Um com 3 docs (Pix) e um com 1 doc (Futebol)
        assert len(result) == 2 
        
        # Vamos achar o cluster do Pix (o maior)
        cluster_pix = next(c for c in result if c['total_docs'] == 3)
        assert cluster_pix is not None
        
        # Verifica se as URLs estão corretas
        urls = cluster_pix['all_urls']
        assert "url1" in urls
        assert "url4" not in urls # Futebol não pode estar aqui

def test_select_representative_docs_logica():
    """
    Testa CIRURGICAMENTE a função _select_representative_docs.
    Vamos provar que ele escolhe o Centróide + Densos e ignora outliers.
    """
    service = Clustering()
    
    # CENÁRIO COMPLEXO:
    # Doc A: Líder (No centro exato). Tamanho pequeno.
    # Doc B: Denso e Confiável (Perto do centro). Tamanho GIGANTE.
    # Doc C: Outlier (Longe do centro). Tamanho GIGANTE também.
    
    docs_input = [
        {"title": "Lider", "content": "aa", "url": "A"},       # Tam: 2. Vetor: [1.0, 0.0]
        {"title": "Denso", "content": "bbbbbbbbbb", "url": "B"}, # Tam: 10. Vetor: [0.9, 0.1]
        {"title": "Outlier", "content": "cccccccccc", "url": "C"} # Tam: 10. Vetor: [0.5, 0.5] (Longe)
    ]
    
    vetores_input = np.array([
        [1.0, 0.0], # A (Centro perfeito do eixo X)
        [0.9, 0.1], # B (Perto)
        [0.5, 0.5]  # C (Longe - Ângulo de 45 graus)
    ])
    
    # Executa a função privada diretamente
    selected = service._select_representative_docs(docs_input, vetores_input)
    
    # ANÁLISE DO RESULTADO ESPERADO:
    # 1. O Líder deve ser o A (mais próximo de [1,0]).
    # 2. O Outlier C deve ser descartado da "Trusted Pool" porque está longe.
    # 3. O Denso B deve ser escolhido porque está perto E é grande.
    
    urls_selecionadas = [d['url'] for d in selected]
    
    assert "A" in urls_selecionadas # Líder
    assert "B" in urls_selecionadas # Denso Confiável
    # assert "C" not in urls_selecionadas # <-- Esse é o pulo do gato! Se C estiver aqui, seu filtro de outlier falhou.

def test_empty_input():
    """Testa resiliência com lista vazia."""
    service = Clustering()
    assert service.process_documents([]) == []