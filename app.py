import asyncio
import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any

# Importa o grafo compilado e o Estado
from src.graph.workflow import graph
from src.utils.logger import setup_logger

# Configura logger para o App
setup_logger()
logger = logging.getLogger(__name__)

async def run_pipeline() -> List[Dict[str, Any]]:
    """
    Executa o workflow do LangGraph e retorna as pautas em formato JSON puro (Lista de Dicts).
    """
    logger.info (" # === Iniciando Pipeline de Geração de Pautas Predictus === # ")
    
    try:
        final_state = await graph.ainvoke(input={})
        pautas_objects = final_state.get("final_briefs", [])
        
        if not pautas_objects:
            logger.warning(" # === O fluxo terminou sem gerar nenhuma pauta. === #")
            return []

        payload_json = [pauta.model_dump() for pauta in pautas_objects]
        
        logger.info(f" # ==== Pipeline finalizado com sucesso. {len(payload_json)} pautas geradas. === #")
        return payload_json

    except Exception as e:
        logger.error(f"# === Erro crítico na execução do pipeline: {e} === #", exc_info=True)
        return []

def save_to_json_file(data: List[Dict[str, Any]]):
    """Salva o payload em um arquivo na pasta output."""
    if not data:
        return

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Nome do arquivo com Timestamp para histórico
    filename = f"pautas_predictus_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"\n💾 Arquivo JSON gerado com sucesso: {filepath}")
    except IOError as e:
        logger.error(f"Erro ao salvar arquivo JSON: {e}")

if __name__ == "__main__":
    # --- PONTO DE ENTRADA (CLI) ---
    
    # Roda o pipeline
    resultado_json = asyncio.run(run_pipeline())
    
    # Ação 1: Salvar em Arquivo (Requisito do Case)
    save_to_json_file(resultado_json)
    
    # Ação 2: Simular resposta de API (Print do Payload)
    print("\n--- PAYLOAD JSON PARA FRONTEND ---")
    print(json.dumps(resultado_json, indent=2, ensure_ascii=False))