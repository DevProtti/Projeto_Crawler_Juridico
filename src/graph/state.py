from pydantic import BaseModel, Field
from typing import List, Optional, Literal


class DocumentObj(BaseModel):
    """
    Representa o objeto bruto obtido durante a coleta de conteúdo em pesquisas e scraping
    (noticias, blogs e outras fontes).  
    Esse objeto é composto a partir da combinação dos resultados do Tavily, feeds RSS
    e extrações realizadas com o Craw4AI.
    """
    title: str = Field(
        ..., 
        description="O título original da notícia ou o h1 da página."
    )
    content: str = Field(
        ..., 
        description="O conteúdo textual limpo (Markdown) extraído da fonte."
    )
    url: str = Field(
        ..., 
        description="A URL de origem para referência"
    )
    published_at: str = Field(
        ..., 
        description="Data de publicação em formato ISO ou string legível."
    )


class ThemeSynthesisOutput(BaseModel):
    """Estrutura exata que o LLM deve preencher ao processar os documentos clusterizados."""
    topic_name: str = Field(
        ..., 
        description="Nome curto e jornalístico do tema (máx 6 palavras). Ex: 'Aumento de Fraudes no Pix'."
    )
    summary: str = Field(
        ..., 
        description="Resumo denso de 2 ou 3 parágrafos consolidando os fatos de todas as fontes."
    )
    reasoning: str = Field(
        ..., 
        description="Explicação técnica do porquê esses documentos foram agrupados (ex: 'Todos tratam da lei X')."
    )
    

class ThemeCluster(BaseModel):
    """
    Representa o tema central de cada cluster encontrado pelo algoritmo de clusterização com base nos 3 principais documentos do cluster
    """
    cluster_id: int = Field(
        ...,
        description="Indicador numérico único do cluster"
    )
    topic_name: str = Field(
        ...,
        description="Título que sumariza/indica o conteúdo sobre aquele determinado cluster. Um nome curto e descritivo para o tema (máx 5 palavras). Ex: 'Novas Regras do Pix'."
    )
    synthesized_summary: str = Field(
        ..., 
        description="Um resumo denso de 2 a 3 parágrafos combinando as informações dos principais documentos do cluster."
    )
    representative_docs: List[DocumentObj] = Field(
        default_factory=list,
        description="Os 3 documentos mais relevantes que deram origem a este cluster."
    )
    score: Optional[float] = Field(
        None, 
        description="Nota de 0 a 100 indicando o quão relevante este tema é para vender os produtos da Predictus."
    )
    reasoning: str = Field(
        ...,
        description="Justificativa do por quê o tema foi aprovado ou rejeitado, levando em consideração os produtos da Predictus. Deve citar produtos específicos quando aprovado"
    )
    

class ContentBrief(BaseModel):
    """
    A pauta estruturada para o time de marketing gerada pelo modelo de IA
    """
    theme_id: int = Field(..., description="ID do cluster que originou esta pauta.")

    title: str = Field(
        ..., 
        description="Um título chamativo otimizado para engajamento e SEO."
    )
    hook: str = Field(
        ..., 
        description="O gancho que conecta a dor do leitor com o tema imediatamente."
    )
    format: Literal["LinkedIn Post", "Blog Article", "Newsletter", "Instagram Post"] = Field(
        ..., 
        description="O formato de conteúdo mais adequado para a complexidade do tema."
    )
    bullet_points: List[str] = Field(
        ..., 
        description="Lista de 3 a 5 tópicos detalhados principais que devem ser abordados no texto."
    )
    target_persona: str = Field(
        ..., 
        description="Para quem é esse texto? Ex: 'Diretores Jurídicos', 'Advogados Autônomos'."
    )


class State(BaseModel):
    search_queries: List[str] = Field(default_factory=list)
    raw_documents: List[DocumentObj] = Field(default_factory=list)
    identified_themes: List[ThemeCluster] = Field(default_factory=list)
    final_briefs: List[ContentBrief] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list)    