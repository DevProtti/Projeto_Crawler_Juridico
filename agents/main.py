import numpy as np
from sklearn.cluster import AgglomerativeClustering
from langchain_openai import OpenAIEmbeddings
from typing import List, Dict

# Assumindo que seu objeto Document tem essa cara:
# class Document:
#     title: str
#     content: str
#     url: str
#     ...

def clustering_node(state: State):
    print("--- INICIANDO CLUSTERING ---")
    documents = state['raw_documents']
    
    if not documents:
        return {"grouped_themes": []}

    # 1. PREPARAÇÃO (A "Impressão Digital")
    # Concatenamos Título + Início do Conteúdo para dar contexto ao embedding
    texts_to_embed = [
        f"Title: {doc.title}\nContent: {doc.content[:1000]}" 
        for doc in documents
    ]

    # 2. VETORIZAÇÃO (Embeddings)
    # Custo baixo: models text-embedding-3-small são muito baratos
    embeddings_model = OpenAIEmbeddings(model="text-embedding-3-small")
    vectors = embeddings_model.embed_documents(texts_to_embed)
    matrix = np.array(vectors)

    # 3. CLUSTERING (Matemática)
    # AgglomerativeClustering com Cosine Distance.
    # distance_threshold=0.4 significa: "Agrupe se a similaridade for maior que ~60/70%"
    # Se mudar para 0.2, ele fica super rigoroso. Se 0.8, agrupa coisas nada a ver.
    cluster_algo = AgglomerativeClustering(
        n_clusters=None,             # Deixa o algoritmo decidir quantos grupos existem
        metric='cosine',             # Essencial para NLP (texto)
        linkage='average',
        distance_threshold=0.4       # <-- O PARÂMETRO DE AJUSTE FINO
    )
    cluster_labels = cluster_algo.fit_predict(matrix)

    # O resultado 'cluster_labels' é algo como: [0, 1, 0, 2, 1]
    # Significa: Doc 0 e Doc 2 são Grupo 0. Doc 1 e Doc 4 são Grupo 1. Doc 3 é Grupo 2.

    # 4. REMAPEAMENTO (Rehydration)
    # Agora voltamos da matemática para os seus dados de negócio
    grouped_map: Dict[int, List[Document]] = {}
    
    for doc, label in zip(documents, cluster_labels):
        if label not in grouped_map:
            grouped_map[label] = []
        grouped_map[label].append(doc)

    # 5. ESTRUTURAÇÃO DO RESULTADO (Lista de Temas)
    final_themes = []
    
    for label, docs_in_cluster in grouped_map.items():
        # Aqui criamos o objeto "Theme" que será passado para o próximo agente
        theme_obj = {
            "cluster_id": int(label),
            "topic_summary": "", # Será preenchido por um LLM no próximo passo se quiser
            "documents": docs_in_cluster, # Guardamos os documentos originais aqui dentro
            "document_count": len(docs_in_cluster)
        }
        final_themes.append(theme_obj)

    print(f"--- CLUSTERING FINALIZADO: {len(final_themes)} TEMAS ENCONTRADOS ---")
    
    # Atualiza o estado do Grafo
    return {"grouped_themes": final_themes}