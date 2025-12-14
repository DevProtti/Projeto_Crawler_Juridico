import os
import json
import logging
from dotenv import load_dotenv, find_dotenv
from pathlib import Path
from typing import Tuple, List, Dict
from supabase import create_client, Client

from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.documents import Document

load_dotenv(find_dotenv())
logger = logging.getLogger(__name__)

# Caminho do arquivo JSON
JSON_PATH = Path(__file__).parent.parent / "config" / "predictus_products.json"

class PredictusKB:
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios.")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        self.vector_store = SupabaseVectorStore(
            client=self.client,
            embedding=self.embeddings,
            table_name="documents",
            query_name="match_documents"
        )
        
        # Sincroniza ao iniciar
        self.sync_knowledge_base()

    def _load_products_from_json(self) -> List[Dict]:
        """Lê e processa o arquivo JSON local."""
        try:
            with open(JSON_PATH, "r", encoding="utf-8") as f:
                products = json.load(f)
            
            processed_data = []
            for p in products:
                # Cria um "Texto Rico" para o vetor entender o contexto completo
                rich_text = (
                    f"Produto: {p['name']}. "
                    f"Descrição: {p['description']} "
                    f"Público Alvo: {p['target_audience']}"
                )
                
                processed_data.append({
                    "name": p["name"],
                    "text": rich_text,
                    # Guardamos os campos originais no metadata para usar depois se precisar
                    "metadata": p 
                })
            return processed_data
        except Exception as e:
            logger.error(f"Erro ao ler predictus_products.json: {e}")
            return []

    def sync_knowledge_base(self):
        """Sincronização Delta (JSON Local -> Supabase)."""
        logger.info("🔄 Sincronizando Base de Conhecimento (JSON -> DB)...")
        
        local_data = self._load_products_from_json()
        if not local_data:
            return

        try:
            # 1. Baixar snapshot atual do banco (apenas IDs e Nomes)
            # Usamos o 'name' dentro do metadata como chave única
            res = self.client.table("documents").select("id, metadata").execute()
            
            # Mapa: Nome do Produto -> ID do Banco
            db_map = {row["metadata"]["name"]: row["id"] for row in res.data}
            
            ids_to_delete = []
            docs_to_add = []

            # 2. Comparar (Estratégia Simples: Substituir Sempre para garantir atualização)
            # Como são poucos produtos, deletar e reinserir quem mudou é barato e seguro.
            
            for item in local_data:
                name = item["name"]
                
                # Se já existe, marcamos para deletar (para inserir a versão nova atualizada)
                if name in db_map:
                    ids_to_delete.append(db_map[name])
                
                # Prepara o novo documento
                doc = Document(
                    page_content=item["text"],
                    metadata=item["metadata"] # Guarda o JSON original no banco
                )
                docs_to_add.append(doc)

            # 3. Executar Mudanças
            if ids_to_delete:
                self.client.table("documents").delete().in_("id", ids_to_delete).execute()
            
            if docs_to_add:
                self.vector_store.add_documents(docs_to_add)
                logger.info(f"✅ Base atualizada: {len(docs_to_add)} produtos sincronizados.")

        except Exception as e:
            logger.error(f"Erro na sincronização: {e}")

    def get_best_match(self, query: str) -> Tuple[str, float]:
        """Busca o produto mais similar."""
        try:
            # 1. Gera os embeddings
            query_vector = self.embeddings.embed_query(query)
            
            # 2. Chamar a função RPC no Supabase direto
            params = {
                "query_embedding": query_vector,
                "match_threshold": 0.0,
                "match_count": 1
            }
            
            response = self.client.rpc("match_documents", params).execute()
            
            # 3. Processar o resultado
            # O response.data é uma lista de dicionários
            if not response.data:
                return "Nenhum Match", 0.0
            
            best_match = response.data[0]
            
            # Extrai metadados e similaridade
            # Nota: Nossa função SQL retorna 'similarity', não 'score'
            name = best_match.get("metadata", {}).get("name", "Desconhecido")
            similarity = best_match.get("similarity", 0.0)
            
            return name, similarity * 100

        except Exception as e:
            logger.error(f"Erro na busca vetorial direta: {e}")
            return "Erro Vetorial", 0.0


if __name__ == "__main__":
    kb_engine = PredictusKB()
