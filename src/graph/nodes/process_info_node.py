# utilitarios
import json
import asyncio
import logging
from typing import Dict, Any, Optional

# Langchain
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Importações internas
from src.core.clustering import cluster_text_documents
from src.graph.state import State, ThemeCluster, ThemeSynthesisOutput
from src.utils.logger import setup_logger
from src.utils.decorators import measure_execution_time

setup_logger()
logger = logging.getLogger(__name__)

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_fallback = ChatOpenAI(model="gpt-4o", temperature=0)
MAX_CONCURRENT_LLM_CALLS = 10


async def _process_single_cluster(cluster_data: Dict[str, Any], semaphore: asyncio.Semaphore) -> Optional[ThemeCluster]:
    """
    Processa um cluster usando Structured Output com Fallback.
    """
    async with semaphore:
        cluster_id = cluster_data['cluster_id']
        rep_docs = cluster_data['representative_docs']

        docs_context_list = []
        print(f"Cluster ID: {cluster_id}")
        for i, doc in enumerate(rep_docs):
            title = doc.title
            content = doc.content
            url = doc.url

            doc_str = (
                f"--- DOCUMENTO #{i+1} ---\n"
                f"Título: {title}\n"
                f"Fonte: {url}\n"
                f"Conteúdo: {content[:2000]}..."
            )
            
            print(doc_str)
            print()
            docs_context_list.append(doc_str)

        full_context = "\n\n".join(docs_context_list)

        prompt = ChatPromptTemplate.from_template("""
        Você é um Analista de Inteligência Sênior.
        Você recebeu um agrupamento de {num_docs} notícias que tratam do mesmo tema.
        
        Sua tarefa é ler TODAS as fontes abaixo e gerar uma síntese unificada.
        
        FONTES:
        {full_context}
        
        INSTRUÇÕES:
        1. Identifique o fato central comum a todas as notícias.
        2. Se houver divergência ou detalhes extras em um documento específico, mencione.
        3. Gere um JSON estrito.

        FORMATO JSON ESPERADO:
        {{
            "topic_name": "Nome curto e jornalístico do tema (máx 6 palavras)",
            "summary": "Resumo denso de 2 ou 3 parágrafos que consolida as informações de todas as fontes.",
            "reasoning": "Explique brevemente por que essas notícias formam um cluster coeso."
        }}
        """)

        main_chain = prompt | llm.with_structured_output(ThemeSynthesisOutput)
        fallback_chain = prompt | llm_fallback.with_structured_output(ThemeSynthesisOutput)

        try:
            result = await main_chain.ainvoke({
                "num_docs": len(rep_docs),
                "full_context": full_context
            })

        except Exception as e:
            logger.warning(f"Falha no modelo primário para cluster {cluster_id}: {e}. Tentando Fallback...")

            try:
                # TENTATIVA 2: Fallback
                result = await fallback_chain.ainvoke({
                    "num_docs": len(rep_docs),
                    "full_context": full_context
                })
                logger.info(f"Recuperado com sucesso via Fallback no cluster {cluster_id}")

            except Exception as error:
                logger.error(f"Erro no cluster {cluster_id} após fallback: {error}")
                return None

        return ThemeCluster(
            cluster_id=cluster_id,
            topic_name=result.topic_name,
            synthesized_summary=result.summary,
            representative_docs=rep_docs,
            reasoning=result.reasoning,
            score=None # Será preenchido no próximo nó
        )


@measure_execution_time
async def process_info_node(state: State) -> dict:
    logger.info(" # ===== INICIO PROCESSAMENTO/CLUSTER ===== #")
    
    # 1. Clusterização
    raw_clusters_dicts = cluster_text_documents(state.raw_documents)
    total = len(raw_clusters_dicts)
    logger.info(f"Clusters matemáticos gerados: {total}")

    if total == 0:
        return {"identified_themes": []}

    # 2. Paralelismo
    semaphore = asyncio.Semaphore(MAX_CONCURRENT_LLM_CALLS)
    tasks = []

    logger.info("Iniciando resumo paralelo dos clusters...")

    for cluster_dict in raw_clusters_dicts:
        tasks.append(_process_single_cluster(cluster_dict, semaphore))

    # 3. Execução
    results = await asyncio.gather(*tasks)
    valid_themes = [res for res in results if res is not None]

    logger.info(f"Resumo concluído. {len(valid_themes)} temas gerados.")
    
    return {"identified_themes": valid_themes}