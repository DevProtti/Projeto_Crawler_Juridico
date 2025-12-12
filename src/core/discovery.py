import asyncio
import aiohttp
import logging 
import feedparser
import os
from datetime import timedelta, date
from typing import List, Dict, Optional
from tavily import AsyncTavilyClient

logger = logging.getLogger(__name__)

from src.config.settings import (
    RSS_FEEDS, 
    TAVILY_QUERIES, 
    TAVILY_API_KEY
)

# --- RSS FEED PARSER SEARCH ENGINE --- #
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
                    "type": "rss",
                    "published_at": pub_date
                })
            return normalized
    except Exception as e:
        logger.error(f"Erro no RSS {url}: {e}")
        return []

async def fetch_rss_feeds() -> List[Dict]:
    """Busca todos os feeds RSS configurados em paralelo."""
    async with aiohttp.ClientSession() as session:
        tasks = [_fetch_single_rss(session, url) for url in RSS_FEEDS]
        results = await asyncio.gather(*tasks)
        flat_results = [item for sublist in results for item in sublist]

        logger.info(f"Busca RSS finalizada. {len(flat_results)} encontrados.")
        return flat_results

# --- TAVILY SEARCH ENGINE --- #
async def fetch_tavily_search(queries: List[str] = None, max_results: int = 5) -> List[Dict]:
    """
    Realiza uma busca assíncrona utilizando Taily sobre temas pré-definidos
    """
    if not TAVILY_API_KEY:
        logger.warning("TAVILY_API_KEY não encontrada. Pulando busca.")
        return []

    try:
        tavily_client = AsyncTavilyClient(api_key=TAVILY_API_KEY)

        tasks = []
        for q in queries:
            tasks.append(
                tavily_client.search(
                    query=q,
                    topic="news", 
                    time_range="month",
                    max_results=max_results, 
                    country="brazil",
                    search_depth="basic"
                )
            )

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        normalized = []

        for res in responses:     
            if isinstance(res, Exception):
                logger.error(f"Erro em uma das buscas Tavily: {res}")
                continue

            results = res.get("results", [])
            valid_items = [
                {
                    "title": item.get('title', ""),
                    "url": item.get('url', ""),
                    "content": item.get('content', ""),
                    "type": "tavily_search",
                    "published_at": item.get("published_date", "")
                }
                for item in results
                if item.get("score", 0) >= 0.75
            ]

            # Adiciona todos de uma vez à lista principal
            normalized.extend(valid_items)

        logger.info(f"Busca Tavily finalizada. {len(normalized)} encontrados.")
        return normalized

    except Exception as e:
        print(f"Erro no Tavily: {e}")
        return []

# --- FUNÇÃO ORQUESTRADORA PARA O LANGGRAPH --- #
async def get_all_initial_documents() -> List[Dict]:
    """
    Função que dispara RSS e Tavily ao mesmo tempo e une os resultados.
    """
    logger.info(f"INÍCIO DA INGESTÃO")
    
    queries = TAVILY_QUERIES[:1]

    results = await asyncio.gather(
        fetch_rss_feeds(),
        fetch_tavily_search(queries, max_results=4)
    )
    
    rss_docs, tavily_docs = results
    
    all_docs = rss_docs + tavily_docs
    return all_docs
 
# --- TESTE RÁPIDO --- #
if __name__ == "__main__":
    from src.utils.logger import setup_logger
    setup_logger()

    docs = asyncio.run(get_all_initial_documents())
    print(docs)