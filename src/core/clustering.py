import numpy as np
import logging
from typing import List, Dict, Any
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics.pairwise import cosine_distances
from collections import defaultdict

logger = logging.getLogger(__name__)

class Clustering:
    def __init__(self, similarity_threshold: float = 0.70):
        self.distance_threshold = 1.0 - similarity_threshold
        self.embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")

    def process_documents(self, documents: List[Dict]) -> List[Dict]:
        """
        Entrada: Lista de dicts normalizados da ingestão.
        Saída: Lista de Clusters enriquecidos com Centróide + 2 documentos mais próximos e Densos.
        """
        if not documents:
            return []

        # 1.Gera textos com os respectivos títulos 
        texts = [f"{d['title']}\n{d['content']}" for d in documents]
        
        # 2. Gera de Embeddings
        vectors = self.embeddings_model.embed_documents(texts)
        matrix = np.array(vectors)

        # 3. Clusterização Hierárquica (Agglomerative)
        # linkage='average' garante que o cluster seja coeso (média das distâncias)
        model = AgglomerativeClustering(
            n_clusters=None, # Define automaticamente
            distance_threshold=self.distance_threshold,
            metric='cosine',
            linkage='average'
        )
        labels = model.fit_predict(matrix)
        
        # 4. Organização dos Grupos
        # caso a chave não exista no dicionário retorna a função lambda para inicialização da chave
        clusters_map = defaultdict(lambda: {"docs": [], "vectors": []}) 
        for idx, label in enumerate(labels):
            clusters_map[label]["docs"].append(documents[idx])
            clusters_map[label]["vectors"].append(matrix[idx])

        # 5. Seleção Estratégica (Centróide + Densos)
        final_themes = []
        for label, data in clusters_map.items():
            cluster_docs = data["docs"]
            cluster_vectors = np.array(data["vectors"])
            
            # Aplica a lógica de seleção dos "Melhores Representantes"
            selected_docs = self._select_representative_docs(cluster_docs, cluster_vectors)
            
            theme_obj = {
                "cluster_id": int(label),
                "total_docs": len(cluster_docs),
                "representative_docs": selected_docs, # Apenas os 3 escolhidos
                "all_urls": [d['url'] for d in cluster_docs] # Para referência
            }
            final_themes.append(theme_obj)

        return final_themes

    def _select_representative_docs(self, docs: List[Dict], vectors: np.ndarray) -> List[Dict]:
        """
        Algoritmo: Depth within Consensus
        1. Acha o Centróide (Média vetorial).
        2. Seleciona o doc mais próximo do centróide (O Líder).
        3. Dentre os vizinhos próximos, seleciona os 2 mais longos (Os Densos).
        """
        # Se o cluster é minúsculo, retorna tudo
        if len(docs) <= 3:
            return docs

        selected = []

        # A. Calcular Centróide e Distâncias
        centroid = np.mean(vectors, axis=0).reshape(1, -1)
        # cosine_distances retorna matriz, pegamos flatten
        dists = cosine_distances(vectors, centroid).flatten()
        
        # B. Identificar o Líder (Menor distância do centro)
        centroid_idx = np.argmin(dists)
        leader_doc = docs[centroid_idx]
        selected.append(leader_doc) # Adiciona o Líder

        # C. Filtrar Candidatos para "Densidade" (Vizinhança Confiável)
        # Queremos documentos que sejam fiéis ao tema (próximos do centro), 
        # mas que sejam longos.
        candidates = []
        for i, doc in enumerate(docs):
            if i == centroid_idx: continue # Pula o líder já escolhido
            
            candidates.append({
                "doc": doc,
                "dist": dists[i],
                "length": len(doc.get('content', ''))
            })
        
        # Ordena por proximidade (Do mais perto para o mais longe)
        candidates.sort(key=lambda x: x['dist'])
        
        # Pega o "Top 50%" mais próximo ou no mínimo 3 candidatos
        # Isso elimina outliers que caíram no cluster por sorte
        pool_size = max(3, len(candidates) // 2)
        trusted_pool = candidates[:pool_size]
        
        # D. Selecionar por Densidade (Tamanho do Texto) dentro da piscina confiável
        trusted_pool.sort(key=lambda x: x['length'], reverse=True)
        
        # Pega os top 2 mais densos
        densest_docs = [item['doc'] for item in trusted_pool[:2]]
        selected.extend(densest_docs)

        return selected

# Wrapper para facilitar importação
def cluster_text_documents(documents: List[Dict]) -> List[Dict]:
    service = Clustering(similarity_threshold=0.70)
    return service.process_documents(documents)