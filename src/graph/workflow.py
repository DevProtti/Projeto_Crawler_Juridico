# utilitarios
import asyncio
import logging
import warnings

# Langgraph
from langgraph.graph import StateGraph, START, END

# Importações internas
from src.graph.state import State, DocumentObj, ThemeCluster, ContentBrief
from src.utils.logger import setup_logger
from src.utils.decorators import measure_execution_time
from src.graph.nodes import ingestion_node, process_info_node, filter_node
#from src.utils.knowledge_base import kb_engine # Importar sua engine do Supabase (se já tiver) ou mocks

warnings.filterwarnings("ignore", message=".*Core Pydantic V1 functionality.*")
setup_logger()
logger = logging.getLogger(__name__)




@measure_execution_time
async def editorial_node(state: State) -> State:
    pass

@measure_execution_time
async def check_relevance(state: State) -> str:
    if state.identified_themes:
        return "editorial"
    return "end"


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
builder.add_edge("ingestion", "process_info")
builder.add_edge("process_info", "filter")
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

if __name__ == "__main__":
    response = asyncio.run(graph.ainvoke(input={}))