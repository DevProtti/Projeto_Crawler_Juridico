# utilitarios
import asyncio
import logging
from typing import List, Optional
from dotenv import find_dotenv, load_dotenv


# Langchain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Importações internas
from src.utils.logger import setup_logger
from src.utils.knowledge_base import PredictusKB
from src.utils.prompts import PROMPT_CHIEF_EDITOR
from src.utils.decorators import measure_execution_time
from src.graph.state import State, ContentBrief, ThemeCluster


load_dotenv(find_dotenv())
setup_logger()
logger = logging.getLogger(__name__)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_fallback = ChatOpenAI(model="gpt-4o", temperature=0)

MAX_CONCURRENT_WRITERS = 10


async def _create_single_brief(
    theme: ThemeCluster, 
    semaphore: asyncio.Semaphore
) -> Optional[ContentBrief]:
    async with semaphore:
        prompt = ChatPromptTemplate.from_template(PROMPT_CHIEF_EDITOR)
        brief: Optional[ContentBrief] = None
        input_data = {
            "theme_id": theme.cluster_id,
            "topic": theme.topic_name,
            "summary": theme.synthesized_summary,
            "reasoning": theme.reasoning
        }
        try:
            chain = prompt | llm.with_structured_output(ContentBrief)
            brief = await chain.ainvoke(input_data)
        except Exception as e:
            logger.warning(f"Erro ao gerar pauta {e}. Tentando novamente com o modelo de fallback...")
            try:
                chain_fallback = prompt | llm_fallback.with_structured_output(ContentBrief)
                brief = await chain_fallback.ainvoke(input_data)
            except Exception as error:
                logger.error(f"Erro fatal ao gerar pauta {error}")

        if brief:
            brief.theme_id = theme.cluster_id
            return brief
        else: 
            return []


@measure_execution_time
async def editorial_node(state: State) -> State:
    logger.info(" # ===== INICIO EDITORIAL / COPYWRITING ===== #")
    
    approved_themes = [theme for theme in state.identified_themes if theme.synthesized_summary]

    if not approved_themes:
        logger.warning("Nenhum tema aprovado para editorial.")
        return {"final_briefs": []}

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_WRITERS)
    tasks = [
        _create_single_brief(theme, semaphore) 
        for theme in approved_themes
    ]

    results = await asyncio.gather(*tasks)
    valid_briefs = [brief for brief in results if brief]

    logger.info(f"Editorial concluído. {len(valid_briefs)} pautas geradas.")
    logger.info(" # ===== FIM EDITORIAL / COPYWRITING ===== #")

    return {"final_briefs": valid_briefs}
        