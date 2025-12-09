# Projeto_Crawler_Juridico

# Diagrama do fluxo de dados


```mermaid
graph TD
    %% Estilos globais
    classDef ingestion fill:#e1f5fe,stroke:#01579b,stroke-width:2px;
    classDef processing fill:#fff9c4,stroke:#fbc02d,stroke-width:2px;
    classDef strategy fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px;
    classDef human fill:#fce4ec,stroke:#880e4f,stroke-width:2px,stroke-dasharray: 5 5;
    classDef storage fill:#f3e5f5,stroke:#4a148c,stroke-width:2px;

    %% Início
    Start((Início)) --> NodeIngestao

    %% 1. Camada de Ingestão (Paralela)
    subgraph "Nó 1: Ingestão Híbrida"
        direction TB
        NodeIngestao[Agente de Ingestão]:::ingestion
        RSS[Leitor de RSS - STF/Conjur]
        Tavily[Busca Tavily - Trends]
        Crawler[Crawl4AI - Extração Markdown]
        
        NodeIngestao --> RSS
        NodeIngestao --> Tavily
        RSS --> Crawler
        Tavily --> Crawler
    end

    %% Conexão
    Crawler --> NodeClustering

    %% 2. Camada de Processamento de Dados
    subgraph "Nó 2: Inteligência de Dados"
        direction TB
        NodeClustering[Agente de Clustering]:::processing
        Embeddings[Geração de Embeddings]
        Algo[Algoritmo Agglomerative]
        Summarizer[LLM: Naming & Summary]

        NodeClustering --> Embeddings
        Embeddings --> Algo
        Algo --> Summarizer
    end

    %% Conexão
    Summarizer --> NodeEstrategia

    %% 3. Camada de Estratégia
    subgraph "Nó 3: Filtro de Produto"
        direction TB
        NodeEstrategia[Agente de Estratégia]:::strategy
        Context[Contexto: Produtos Predictus]
        Score[Scoring & Relevância]

        NodeEstrategia -.-> Context
        NodeEstrategia --> Score
    end

    %% Decisão Condicional
    Score --> CheckRelevance{Score > 70?}
    CheckRelevance -- Não --> Discard[Descartar/Monitorar]:::storage
    CheckRelevance -- Sim --> NodePautas

    %% 4. Camada de Criação
    subgraph "Nó 4: Editor Chefe"
        NodePautas[Gerador de Pautas]:::strategy
        Briefing[Criação de Título/Formato/Bullets]
        NodePautas --> Briefing
    end

    %% 5. Human in the Loop
    Briefing --> HumanReview[👤 Revisão Humana]:::human
    
    %% Loop de Correção
    HumanReview -- Rejeitar/Refazer --> NodePautas
    HumanReview -- Aprovar --> NodePersistencia

    %% 6. Finalização
    NodePersistencia[Gravação BD / Vector DB]:::storage --> End((Fim))

```