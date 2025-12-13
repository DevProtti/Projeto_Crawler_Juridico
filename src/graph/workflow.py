import asyncio
from pydantic import BaseModel
from langgraph.graph import StateGraph, START, END
from src.core.discovery import get_all_initial_documents
from src.core.extractor import batch_extract_contents
from state import State, DocumentObj, ThemeCluster, ContentBrief
import logging

logger = logging.getLogger(__name__)

async def ingestion_node(state: State) -> State: 
    response = await get_all_initial_documents()

    docs_objects = []
    for result in response:
        try:
            doc_obj = DocumentObj(**result)
            docs_objects.append(doc_obj)
        except Exception as e:
            logger.error(f"Erro ao validar documento {result.get('url', '?')}: {e}")
            continue

    return {"raw_documents": docs_objects}
        

async def process_info_node(state: State)-> State:
    urls = [document.url for document in state.raw_documents]
    cluster_classes = await batch_extract_contents(urls)



async def filter_node(state: State) -> State:
    # TODO Filtrar os temas que tem relevância com o produto
    pass

async def editorial_node(state: State) -> State: 
    pass


async def check_relevance(state: State) -> str:
    pass


# --- CONSTRUÇÃO DO GRAFO --- #

# Inicialização do contrutor com schema Pydantic
builder = StateGraph(State)

# Adiconando nodes
builder.add_node("ingestion", ingestion_node)
builder.add_node("process_info", process_info_node)
builder.add_node("filter", filter_node)
builder.add_node("editorial", editorial_node)

# Adicionando edges
builder.add_edge(START, "ingestion")
builder.add_edge("ingestion", "processing")
builder.add_edge("processing", "filter")
builder.add_conditional_edges(
    "filter",
    check_relevance,
    {
        "editorial": "editorial",
        "end": END
    }
)
builder.add_edge("editorial", END)

# Compilando o grafo
graph = builder.compile()