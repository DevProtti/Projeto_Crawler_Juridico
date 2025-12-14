import numpy as np
import logging
from typing import List, Dict
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances
from collections import defaultdict
from sklearn.metrics import silhouette_score
from src.graph.state import DocumentObj
from dotenv import load_dotenv, find_dotenv


load_dotenv(find_dotenv())


logger = logging.getLogger(__name__)

class Clustering:
    def __init__(self, similarity_threshold: float = 0.50):
        self.distance_threshold = 1.0 - similarity_threshold    
        self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

    def process_documents(self, documents: List[DocumentObj]) -> List[Dict]:
        """
        Entrada: Lista de DocumentObj normalizados da ingestão.
        Saída: Lista de Clusters enriquecidos com Centróide + 2 documentos mais próximos e Densos.
        """
        if not documents:
            return []

        texts = [f"{d.title}\n{d.content}" for d in documents]
        vectors = self.embeddings_model.embed_documents(texts)
        matrix = np.array(vectors)

        # linkage='average' garante que o cluster seja coeso (média das distâncias)
        model = AgglomerativeClustering(
            n_clusters=None, # Define automaticamente
            # distance_threshold=self.distance_threshold,
            distance_threshold=0.29,
            metric='cosine',
            linkage='average'
        )
        try:
            labels = model.fit_predict(matrix)
        except Exception as e:
            logger.error(f"Um erro ocorreou ao tentar clusterizar os textos {e}")
        

        unique_labels = set(labels)
        if len(unique_labels) > 1:
            score = silhouette_score(matrix, labels, metric="cosine")
            logger.info(f"QUALIDADE DO CLUSTER (Silhouette Score): {score:.4f}")
        else:
            logger.warning("Silhouette Score não calculado: Apenas 1 cluster detectado.")

        # caso a chave não exista no dicionário retorna a função lambda para inicialização da chave
        clusters_map = defaultdict(lambda: {"docs": [], "vectors": []}) 
        for idx, label in enumerate(labels):
            clusters_map[label]["docs"].append(documents[idx])
            clusters_map[label]["vectors"].append(matrix[idx])

        final_clusters = []
        for label, data in clusters_map.items():
            cluster_docs = data["docs"]
            cluster_vectors = np.array(data["vectors"])
            
            # Aplica a lógica de seleção dos "Melhores Representantes"
            selected_docs: List[DocumentObj] = self._select_representative_docs(cluster_docs, cluster_vectors)
            
            cluster_obj = {
                "cluster_id": int(label),
                "total_docs": len(cluster_docs),
                "representative_docs": selected_docs,
                "all_urls": [d.url for d in cluster_docs]
            }
            final_clusters.append(cluster_obj)

        return final_clusters

    def _select_representative_docs(self, docs: List[DocumentObj], vectors: np.ndarray) -> List[Dict]:
        """
        1. Acha o Centróide dentro do cluster (Média vetorial).
        2. Seleciona o doc mais próximo do centróide.
        3. Dentre os vizinhos próximos (raio de 50%), seleciona os 2 mais longos (Os Densos).
        """
        # Se o cluster é minúsculo, retorna tudo
        if len(docs) <= 3:
            return docs

        selected = []

        # Calcular Centróide e Distâncias
        centroid = np.mean(vectors, axis=0).reshape(1, -1)
        # cosine_distances retorna matriz
        dists = cosine_distances(vectors, centroid).flatten()
        
        # Identificar o Líder (Menor distância do centro)
        centroid_idx = np.argmin(dists)
        leader_doc = docs[centroid_idx]
        selected.append(leader_doc)

        # Filtrar Candidatos para "Densidade" (Vizinhança Confiável)
        # Queremos documentos que sejam fiéis ao tema (próximos do centro), mas que sejam longos.
        candidates = []
        for i, doc in enumerate(docs):
            if i == centroid_idx: continue 
            
            candidates.append({
                "doc": doc,
                "dist": dists[i],
                "length": len(doc.content)
            })
        
        # Ordena por proximidade (Do mais perto para o mais longe)
        candidates.sort(key=lambda x: x['dist'])
        
        # Pega o "Top 50%" mais próximo ou no mínimo 3 candidatos
        # Isso elimina outliers que caíram no cluster por sorte
        pool_size = max(3, len(candidates) // 2)
        trusted_pool = candidates[:pool_size]
        
        # Selecionar por Densidade (Tamanho do Texto) dentro da piscina confiável
        trusted_pool.sort(key=lambda x: x['length'], reverse=True)
        
        # Pega os top 2 mais densos
        densest_docs = [item['doc'] for item in trusted_pool[:2]]
        selected.extend(densest_docs)

        return selected


def cluster_text_documents(documents: List[DocumentObj]) -> List[Dict]:
    logger.info("# =====  PROCESSO DE CLUSTERIZAÇÃO INICIADO ===== #")
    
    service = Clustering(similarity_threshold=0.85)
    generated_clusters = service.process_documents(documents)

    logger.info("# =====  PROCESSO DE CLUSTERIZAÇÃO FINALIZADO ===== #")

    return generated_clusters

if __name__ == "__main__":
    from src.utils.texts import TEXTO_1, TEXTO_2, TEXTO_3, TEXTO_4, TEXTO_5
    from src.utils.logger import setup_logger
    
    setup_logger()

    documents = [
        DocumentObj(
            title="Jurimetria e Inteligência Artificial: A Revolução Quantitativa no Direito", 
            url="https://texto_1", 
            content=TEXTO_1, 
            published_at="2025-12-12"
        ),
        DocumentObj(
            title="Jurimetria Comum e Jurimetria Preditiva: Duas Abordagens Complementares", 
            url="https://texto_2", 
            content=TEXTO_2, 
            published_at="2025-12-12"
        ),
        DocumentObj(
            title="Legal Analytics: A Inteligência de Dados Transformando a Advocacia Corporativa", 
            url="https://texto_3", 
            content=TEXTO_3,
            published_at="2025-12-12"
        ),

        DocumentObj(
            title="Jurimetria Aplicada à Análise de Score de Crédito: Quantificando Riscos Jurídicos no Sistema Financeiro", 
            url="https://texto_4", 
            content=TEXTO_4,
            published_at="2025-12-12"
        ),

        DocumentObj(
            title="Arcabouço Fiscal de 2025: Desafios da Implementação e Perspectivas", 
            url="https://texto_5", 
            content=TEXTO_5,
            published_at="2025-12-12"
        ),
    ]

    clusters = cluster_text_documents(documents)

    print(f"\nTotal de Clusters gerados: {len(clusters)}")
    for cluster in clusters:
        print(f"Cluster {cluster['cluster_id']}: {cluster['total_docs']} documentos. (URLs: {cluster['all_urls']})")