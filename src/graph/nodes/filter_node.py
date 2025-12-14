# utilitarios
import asyncio
import logging
import warnings

# Langchain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Importações internas
from src.graph.state import State, DocumentObj, ThemeCluster, ContentBrief
from src.utils.logger import setup_logger
from src.utils.decorators import measure_execution_time


setup_logger()
logger = logging.getLogger(__name__)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_fallback = ChatOpenAI(model="gpt-4o", temperature=0)

@measure_execution_time
async def filter_node(state: State) -> State:
    identified_themes = state.identified_themes

    for theme in identified_themes:
        print(theme)
        print("="*100)
        print("\n")
