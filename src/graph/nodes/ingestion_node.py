# utilitários
import logging

# Importações internas
from src.core.discovery import get_all_initial_documents
from src.core.extractor import batch_extract_contents
from src.graph.state import State, DocumentObj
from src.utils.logger import setup_logger
from src.utils.decorators import measure_execution_time

setup_logger()
logger = logging.getLogger(__name__)

@measure_execution_time
async def ingestion_node(state: State) -> State: 
    logger.info(" # ===== INICIO INGESTAO ===== #")

    searched_raw_docs = await get_all_initial_documents()
    unique_docs_map = {doc["url"]: doc for doc in searched_raw_docs if doc.get("url")}
    searched_docs = list(unique_docs_map.values())
    urls = list(unique_docs_map.keys())
    scrapped_documents = await batch_extract_contents(urls, max_concurrent=10)

    scrapped_map = {doc["url"]: doc for doc in scrapped_documents if "url" in doc}

    docs_objects = []
    for searched_doc in searched_docs:  
        url_key = searched_doc.get("url")
        scrapped_data = scrapped_map.get(url_key)

        if scrapped_data:
            new_dict = {
                "title": searched_doc.get("title"),
                "url": url_key,
                "source_type": searched_doc.get("type"),
                "published_at": searched_doc.get("published_at"),
                "content": scrapped_data.get("content")
            }
            docs_objects.append(DocumentObj(**new_dict))
        else:
            # Opcional: Logar se não houve scrape para esta URL
            logger.warning(f"Conteúdo não encontrado para: {url_key}")

    logger.info(" # ===== FIM INGESTAO ===== #")

    return {"raw_documents": docs_objects}