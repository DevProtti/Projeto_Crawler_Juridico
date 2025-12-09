"""
Código corrigido para usar Ollama com crawl4ai

PROBLEMA IDENTIFICADO:
1. O parâmetro estava como 'llmConfig' (C maiúsculo) mas deveria ser 'llm_config' (com underscore)
2. Para Ollama, é recomendado definir api_token=None explicitamente

SOLUÇÃO:
"""

import os
import json
import asyncio
from typing import List
from pydantic import BaseModel, Field
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, LLMConfig
from crawl4ai import LLMExtractionStrategy

class Entity(BaseModel):
    name: str
    description: str

class Relationship(BaseModel):
    entity1: Entity
    entity2: Entity
    description: str
    relation_type: str

class KnowledgeGraph(BaseModel):
    entities: List[Entity]
    relationships: List[Relationship]

async def main():
    # LLM extraction strategy
    # CORREÇÃO: llmConfig -> llm_config (com underscore)
    # Para Ollama, api_token pode ser None
    llm_strat = LLMExtractionStrategy(
        llm_config=LLMConfig(  # CORRIGIDO: era llmConfig, agora é llm_config
            provider="ollama/llama3.2",
            base_url="http://localhost:11434",
            api_token=None  # Ollama não requer API key
        ),
        schema=KnowledgeGraph.model_json_schema(),
        extraction_type="schema",
        instruction="Extract entities and relationships from the content. Return valid JSON.",
        chunk_token_threshold=1400,
        apply_chunking=True,
        input_format="html",
        extra_args={"temperature": 0.1, "max_tokens": 2000}
    )

    crawl_config = CrawlerRunConfig(
        extraction_strategy=llm_strat,
        cache_mode=CacheMode.BYPASS
    )

    async with AsyncWebCrawler(config=BrowserConfig(headless=True)) as crawler:
        # Example page
        url = "https://www.jusbrasil.com.br/noticias/"
        result = await crawler.arun(url=url, config=crawl_config)

        print("--- LLM RAW RESPONSE ---")
        print(result.extracted_content)
        print("--- END LLM RAW RESPONSE ---")

        if result.success:
            with open("kb_result.json", "w", encoding="utf-8") as f:
                f.write(result.extracted_content)
            llm_strat.show_usage()
        else:
            print("Crawl failed:", result.error_message)


if __name__ == "__main__":
    asyncio.run(main())

