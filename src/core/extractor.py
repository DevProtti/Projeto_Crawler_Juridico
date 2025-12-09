import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from typing_extensions import List, Dict


async def extract_content_from_url(url: str) -> str:
    """
    Acessa uma URL específica e extrai o conteúdo principal em Markdown.
    """
    try:

        prune_filter = PruningContentFilter(
            # Lower → more content retained, higher → more content pruned
            threshold=0.45,
            threshold_type="dynamic",
            min_word_threshold=5      
        )   

        md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)
        config = CrawlerRunConfig(
            markdown_generator=md_generator
        )

        # O crawl4ai gerencia o navegador internamente
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(
                url=url,
                config=config
            )
            
            if result.success:
                return result.markdown.fit_markdown
            else:
                print(f"Falha ao extrair {url}: {result.error_message}")
                return ""
    except Exception as e:
        print(f"Erro crítico no crawl4ai para {url}: {e}")
        return ""

async def batch_extract_contents(urls: List[str], max_concurrent: int = 5) -> Dict[str, str]:
    """
    Processa várias URLs com limitação de concorrência para evitar overload de RAM.
    """
    
    results = {}
    semaphore = asyncio.Semaphore(max_concurrent)

    async def semaphore_task(url):
        async with semaphore:
            return url, await extract_content_from_url(url)
    
    tasks = [semaphore_task(url) for url in urls]
    contents = await asyncio.gather(*tasks)
    
    if contents:
        for content in contents:
            results[f"{content[0]}"] = f"{content[1]}"

        
    return results

if __name__ == '__main__':
    from src.core.discovery import get_all_initial_documents


    searched_items = asyncio.run(get_all_initial_documents())
    urls = [item.get("url", "") for item in searched_items[:10]]
    results = asyncio.run(batch_extract_contents(urls=urls))

    for url, content in results.items():
        print(f"URL: {url}")
        print(f"Markdown:\n\n{content}\n\n")
        print("==="*50)




