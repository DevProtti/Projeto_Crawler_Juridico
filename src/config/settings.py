from datetime import datetime
import os
from dotenv import load_dotenv
from src.config.queries_tavily import queries_combinadas

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

TAVILY_QUERIES = queries_combinadas


COSSINE_SIMILARITY_THRESHOLD = 0.7