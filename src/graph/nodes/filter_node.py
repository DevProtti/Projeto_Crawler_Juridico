# utilitarios
import logging
from typing import List, Optional
from dotenv import find_dotenv, load_dotenv

# Langchain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Importações internas
from src.utils.logger import setup_logger
from src.utils.knowledge_base import PredictusKB
from src.utils.prompts import PROMPT_PRODUCT_MANAGER
from src.utils.decorators import measure_execution_time
from src.graph.state import State, ThemeCluster, StrategicReasoning

load_dotenv(find_dotenv())
setup_logger()
logger = logging.getLogger(__name__)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_fallback = ChatOpenAI(model="gpt-4o", temperature=0)


@measure_execution_time
async def filter_node(state: State) -> dict:
    logger.info(" # ===== INICIO FILTRO VETORIAL + ESTRATÉGICO ===== #")
    
    approved_themes: List[ThemeCluster] = []
    MIN_VECTOR_SCORE = 40.0
    kb_engine = PredictusKB()

    for theme in state.identified_themes:
        # Verifica por similaridade de cosseno se o vetor do sumário do cluster tem relação com agum dos produtos da Predictus
        best_product_name, vector_score = kb_engine.get_best_match(theme.synthesized_summary)
        logger.info(f"Tema: '{theme.topic_name}' | Match: '{best_product_name}' | Score: {vector_score:.2f}%")

        if vector_score < MIN_VECTOR_SCORE:
            logger.info(f"Rejeitado por score baixo ({vector_score:.1f} < {MIN_VECTOR_SCORE})")
            continue
        
        prompt = ChatPromptTemplate.from_template(PROMPT_PRODUCT_MANAGER)
        
        chain = prompt | llm.with_structured_output(StrategicReasoning)
        chain_fallback = prompt | llm_fallback.with_structured_output(StrategicReasoning)

        analysis: Optional[StrategicReasoning] = None
        input_data = {
            "vector_score": vector_score,
            "product_name": best_product_name,
            "title": theme.topic_name,
            "summary": theme.synthesized_summary
        }
        try:
            analysis = await chain.ainvoke(input_data)
            
        except Exception as e:
            logger.warning(f"Erro na análise estratégica do tema {theme.topic_name}: {e}. Tentando novamente com o modelo de fallback") 
            try:
                analysis = await chain_fallback.ainvoke(input_data)

            except Exception as error:
                logger.info(f"Erro fatal na análise estratégica do tema {theme.topic_name}: {error}.")
                continue
       
        if analysis:
            theme.score = analysis.final_score
            theme.reasoning = analysis.reasoning
            
            if theme.score >= 40:
                approved_themes.append(theme)
            else:
               logger.warning(f"Vetor aprovou ({vector_score:.1f}%), mas LLM rejeitou ({theme.score}): {theme.topic_name}")

    logger.info(f"Filtro concluído. {len(approved_themes)} de {len(state.identified_themes)} temas avançaram.")
    logger.info(" # ===== FIM FILTRO VETORIAL + ESTRATÉGICO ===== #")
    
    return {"identified_themes": approved_themes}
