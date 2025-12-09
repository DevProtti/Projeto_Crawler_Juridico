import asyncio
import aiohttp
import logging 
import feedparser
import os
from datetime import timedelta, date
from typing import List, Dict, Optional
from tavily import TavilyClient

logger = logging.getLogger(__name__)

from src.config.settings import (
    RSS_FEEDS, 
    TAVILY_QUERIES, 
    TAVILY_API_KEY
)

# --- RSS FEED PARSER SEARCH ENGINE ---

async def _fetch_single_rss(session: aiohttp.ClientSession, url: str) -> List[Dict]:
    """Busca e normaliza as URL buscadas um único feed RSS."""
    try:
        async with session.get(url, timeout=10) as response:
            if response.status != 200:
                logger.error(f"Erro {response.status} ao acessar {url}")
                return []
            
            content = await response.text()
            feed = feedparser.parse(content)
            
            normalized = []
            for entry in feed.entries:
                summary = entry.get('summary', entry.get('description', ''))
                pub_date = entry.get('published', entry.get('updated', 'Data desconhecida'))
                
                normalized.append({
                    "title": entry.title,
                    "url": entry.link,
                    "content": summary,
                    "source": feed.feed.get('title', 'Fonte RSS'),
                    "type": "rss",
                    "published_at": pub_date
                })
            return normalized
    except Exception as e:
        print(f"Erro no RSS {url}: {e}")
        logger.error(f"Erro no RSS {url}: {e}")
        return []

async def fetch_rss_feeds() -> List[Dict]:
    """Busca todos os feeds RSS configurados em paralelo."""
    async with aiohttp.ClientSession() as session:
        tasks = [_fetch_single_rss(session, url) for url in RSS_FEEDS]
        results = await asyncio.gather(*tasks)
        
        # Colocar resultados dentro de somente uma lista
        flat_results = [item for sublist in results for item in sublist]

        logger.info(f"Busca RSS finalizada. {len(flat_results)} encontrados.")
        return flat_results

# --- TAVILY SEARCH ENGINE ---

def fetch_dates():
    today = date.today()
    previous_month = today - timedelta(days=90)

    return (str(today), str(previous_month))


async def fetch_tavily_search(queries: List[str] = None, max_results: int = 5) -> List[Dict]:
    """
    Realiza uma busca assíncrona utilizando Taily sobre temas pré-definidos
    """
    if not TAVILY_API_KEY:
        print("TAVILY_API_KEY não encontrada. Pulando busca.")
        return []

    try:
        date_today, date_today_minus_90_days = fetch_dates()   
        tavily_client = TavilyClient(api_key=TAVILY_API_KEY)

        tasks = []
        for q in queries:
            tasks.append(
                asyncio.to_thread(
                    tavily_client.search,
                    query=q,
                    max_results=max_results, 
                    start_date=date_today_minus_90_days, 
                    end_date=date_today,
                    country="brazil" 
                )
            )

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        normalized = []

        for res in responses:           
            if isinstance(res, Exception):
                logger.error(f"Erro em uma das buscas Tavily: {res}")
                continue
            
            if "results" in res and res["results"]:
                for item in res["results"]:
                    if item.get("score", 0) >= 0.75:
                        normalized.append({
                            "title": item.get('title'),
                            "url": item.get('url'),
                            "content": item.get('content'),
                            "source": "Tavily Search",
                            "type": "tavily_search",
                            "published_at": f"Entre {date_today_minus_90_days} e {date_today}"
                        })

        logger.info(f"Busca Tavily finalizada. {len(normalized)} encontrados.")
        return normalized

    except Exception as e:
        print(f"Erro no Tavily: {e}")
        return []

# --- FUNÇÃO ORQUESTRADORA PARA O LANGGRAPH ---

async def get_all_initial_documents() -> List[Dict]:
    """
    Função Mestra: Dispara RSS e Tavily ao mesmo tempo e une os resultados.
    Esta é a única função que seu LangGraph precisa chamar.
    """
    logger.info(f"INÍCIO DA INGESTÃO")
    
    queries = TAVILY_QUERIES[:1]

    # Roda RSS e Tavily em paralelo
    results = await asyncio.gather(
        fetch_rss_feeds(),
        fetch_tavily_search(queries, max_results=4)
    )
    
    rss_docs, tavily_docs = results
    
    # Unificação
    all_docs = rss_docs + tavily_docs
    return all_docs
 
# --- TESTE RÁPIDO (Executar direto este arquivo) ---
if __name__ == "__main__":
    from src.utils.logger import setup_logger
    setup_logger()

    docs = asyncio.run(get_all_initial_documents())
    print(docs)