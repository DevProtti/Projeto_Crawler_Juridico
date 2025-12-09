import os
from dotenv import load_dotenv

load_dotenv()


LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()

# Chaves de API
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

RSS_FEEDS = [
    # Tier 1: Tribunais (Fatos Oficiais)
    "https://res.stj.jus.br/hrestp-c-portalp/RSS.xml",
    
    # Tier 2: Mídia Jurídica (Análise/Buzz)
    "https://www.conjur.com.br/rss.xml",
    "https://www.migalhas.com.br/rss/rss.xml",
    
    # Tier 3: Legislativo
    "https://www.camara.leg.br/noticias/rss/ultimas-noticias"
]

TAVILY_QUERIES = [
    # Jurimetria
    "Impacto prático da inteligência artificial e jurimetria nas decisões judiciais recentes no Brasil",
    "Dados recentes sobre a morosidade do judiciário brasileiro e seus impactos financeiros nas empresas",
    "Tendências atuais de legal analytics para redução de passivo trabalhista e cível",
    "Cases de sucesso sobre uso de dados para previsão de sentenças judiciais no Brasil",
    "Alterações recentes na jurisprudência do STJ que impactam o setor de varejo e bancário",
    
    # Risco e Fraude
    "Notícias recentes sobre o aumento de fraudes corporativas e uso de laranjas em empresas brasileiras",
    "Novas regulamentações de compliance e due diligence para contratação de fornecedores no Brasil",
    "Casos recentes de prejuízos por falhas em background check e validação cadastral corporativa",
    "Índices atuais de inadimplência e fraudes financeiras afetando grandes empresas no Brasil",
    "Novas regras de prevenção à lavagem de dinheiro impactando advogados e departamentos jurídicos",
    
    #  Benchmarking e Gestão de Escritórios
    "Critérios atuais utilizados por grandes empresas para contratar escritórios de advocacia baseados em dados",
    "Principais KPIs e métricas de eficiência utilizadas por departamentos jurídicos de alta performance",
    "Tendências em benchmarking jurídico e avaliação de desempenho de advogados terceirizados",

    # Legal Ops / Automação
    "Tendências de crescimento de Legal Ops e hiperautomação jurídica no Brasil",
    "Ferramentas e estratégias para redução de custos operacionais em departamentos jurídicos",
    "Desafios atuais de integração de dados e interoperabilidade na transformação digital jurídica",
    
    # Buzz
    "Maiores condenações judiciais e indenizações contra empresas brasileiras nos últimos meses",
    "Setores da economia com maior volume de novos processos judiciais no Brasil atualmente",
    "Tecnologias emergentes essenciais para gestão de risco jurídico e compliance corporativo"
]


COSSINE_SIMILARITY_THRESHOLD = 0.7