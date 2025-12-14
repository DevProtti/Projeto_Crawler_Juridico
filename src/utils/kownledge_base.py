import os
import logging
from typing import Tuple
from supabase import create_client, Client
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.documents import Document

logger = logging.getLogger(__name__)

# TODO - Montar o fluxo com Pydantic, Tavily e Craw4AI para buscar informações relevantes de produto e ICP da Predictus
PREDICTUS_DATA = [
    # PRODUTOS
    {"text": "Produto: Jurimetria Predictus. Software de análise preditiva para prever sentenças e resultados de processos judiciais usando estatística.", "name": "Jurimetria"},
    {"text": "Produto: Dossiê Cadastral. Ferramenta de Background Check para compliance, validação de fornecedores e prevenção a fraudes.", "name": "Dossie Cadastral"},
    {"text": "Produto: API de Processos. Integração automática de dados judiciais em sistemas de terceiros via API REST.", "name": "API de Processos"},
    
    # PERSONAS
    {"text": "Persona: Diretor Jurídico de Varejo. Preocupado com alto volume de processos trabalhistas e custos de indenização.", "name": "Diretor Juridico Varejo"},
    {"text": "Persona: Sócio de Escritório de Advocacia. Busca eficiência operacional, automação de peças e captar grandes clientes.", "name": "Socio Advocacia"},
    {"text": "Persona: Gerente de Compliance. Focado em prevenir lavagem de dinheiro, fraudes e riscos reputacionais.", "name": "Gerente Compliance"}
]

class PredictusKB:
    def __init__(self):

        # TODO - Verificar como fazer conexão com o Supabase
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios.")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        
        # --- A MÁGICA DO LANGCHAIN ---
        # Instanciamos o VectorStore conectado ao Supabase
        self.vector_store = SupabaseVectorStore(
            client=self.client,
            embedding=self.embeddings,
            table_name="documents",       # Nome da tabela criada no SQL
            query_name="match_documents"  # Nome da função criada no SQL
        )
        
        self._ensure_populated()

    def _ensure_populated(self):
        """Verifica se o banco está vazio e insere os dados iniciais."""
        try:
            # Verificação leve usando cliente bruto
            res = self.client.table("documents").select("id", count="exact").limit(1).execute()
            
            if res.count == 0:
                logger.info("🏗️ Populando Knowledge Base via LangChain...")
                
                # Prepara documentos no formato LangChain
                docs = [
                    Document(page_content=item["text"], metadata={"name": item["name"]})
                    for item in PREDICTUS_DATA
                ]
                
                # O LangChain faz tudo: gera embedding e insere no Supabase
                self.vector_store.add_documents(docs)
                
                logger.info(f"✅ {len(docs)} itens inseridos na Base de Conhecimento.")
            else:
                logger.info("📚 Knowledge Base já carregada.")
                
        except Exception as e:
            logger.error(f"Erro ao inicializar KB: {e}")

    def get_best_match(self, query: str) -> Tuple[str, float]:
        """
        Recebe um texto (resumo do tema) e retorna o produto/persona mais similar.
        Retorna: (Nome do Produto, Score 0-100)
        """
        # O LangChain faz o embedding da query e busca no banco
        results = self.vector_store.similarity_search_with_relevance_scores(
            query=query,
            k=1  # Queremos apenas o melhor match
        )
        
        if not results:
            return "Nenhum Match", 0.0
            
        doc, score = results[0]
        
        # O score vem normalizado (0 a 1). Multiplicamos por 100.
        return doc.metadata.get("name", "Desconhecido"), score * 100

# Instância Global
kb_engine = PredictusKB()