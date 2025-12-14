import logging
import os
from supabase import create_client, Client
from src.graph.state import State

logger = logging.getLogger(__name__)

# Inicialização do Cliente Supabase (Singleton simples)
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

async def save_node(state: State) -> dict:
    logger.info(" # ===== INICIO PERSISTÊNCIA (DB) ===== #")
    
    # 1. Salvar Documentos Brutos (Raw Content)
    if state.raw_documents:
        logger.info(f"Salvando {len(state.raw_documents)} documentos brutos...")
        raw_data = []
        for doc in state.raw_documents:
            raw_data.append({
                "url": doc.url,
                "title": doc.title,
                "content": doc.content,
                "published_at": doc.published_at,
                "source_type": doc.source_type
            })
        
        try:
            supabase.table("raw_contents").upsert(raw_data, on_conflict="url").execute()
        except Exception as e:
            logger.error(f"Erro ao salvar documentos brutos: {e}")

    # 2. Salvar Temas e Pautas (Relacionamento)    
    saved_briefs_count = 0
    
    for brief in state.final_briefs:
        original_theme = next(
            (t for t in state.identified_themes if t.cluster_id == brief.theme_id), 
            None
        )
        
        if not original_theme:
            logger.warning(f"Pauta '{brief.title}' sem tema correspondente encontrado. Pulando.")
            continue

        try:
            # A. Inserir o TEMA na tabela 'themes' e retornar o ID gerado
            theme_payload = {
                "topic_name": original_theme.topic_name,
                "summary": original_theme.synthesized_summary,
                "score": original_theme.score,
                "reasoning": original_theme.reasoning
            }
            
            theme_res = supabase.table("themes").insert(theme_payload).execute()
            
            if not theme_res.data:
                continue
                
            real_db_theme_id = theme_res.data[0]['id']

            # B. Inserir a PAUTA na tabela 'content_briefs' usando o ID real
            brief_payload = {
                "theme_id": real_db_theme_id, # FK real do banco
                "title": brief.title,
                "hook": brief.hook,
                "format": brief.format,
                "target_persona": brief.target_persona,
                "bullet_points": brief.bullet_points # Supabase aceita lista direta para JSONB
            }
            
            supabase.table("content_briefs").insert(brief_payload).execute()
            saved_briefs_count += 1
            
        except Exception as e:
            logger.error(f"Erro ao persistir par Tema/Pauta: {e}")

    logger.info(f"Persistência concluída. {saved_briefs_count} pautas gravadas no banco.")
    logger.info(" # ===== FIM PERSISTÊNCIA ===== #")
    
    return {} # Não precisamos atualizar o state, é o fim da linha.