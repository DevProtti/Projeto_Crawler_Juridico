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
        description="A URL de origem para referência e fact-checking."
    )
    source: str = Field(
        ..., 
        description="Nome da fonte (ex: 'STF', 'Conjur', 'Youtube')."
    )
    published_at: str = Field(
        ..., 
        description="Data de publicação em formato ISO ou string legível."
    )

class ThemeCluster(BaseModel):
    pass

class ContentBrief(BaseModel):
    pass

class State(BaseModel):
    pass    