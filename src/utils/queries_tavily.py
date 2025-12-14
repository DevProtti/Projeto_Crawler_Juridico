from datetime import datetime

# Data atual para interpolação
data_atual = datetime.now()
ano_atual = data_atual.year
mes_atual = data_atual.month
data_formatada = data_atual.strftime("%Y-%m-%d")

# ============================================================================
# QUERIES PARA TAVILY - MARKETING PREDICTUS
# ============================================================================

# ----------------------------------------------------------------------------
# 1. TENDÊNCIAS E NOVIDADES DO MERCADO JURÍDICO
# ----------------------------------------------------------------------------
tendencias_mercado = [
    f"legal tech trends {ano_atual} Brazil",
    "transformação digital advocacia Brasil",
    "inteligência artificial direito casos uso",
    "jurimetria aplicações práticas",
    "API dados judiciais mercado",
    f"inovação legal tech {ano_atual}",
    f"futuro advocacia {ano_atual}",
    "tecnologia tribunais Brasil",
    f"legal tech Brasil crescimento {ano_atual}",
    "automação processos jurídicos tendências"
]

# ----------------------------------------------------------------------------
# 2. DORES E DESAFIOS DO PÚBLICO-ALVO
# ----------------------------------------------------------------------------
dores_desafios = [
    "desafios análise risco jurídico empresas",
    "problemas due diligence departamentos jurídicos",
    "dificuldades acesso dados processos judiciais",
    "compliance jurídico desafios Brasil",
    "background check jurídico empresas",
    "provisionamento contingências jurídicas dificuldades",
    "gestão riscos legais empresas brasileiras",
    "custos litígio empresas Brasil",
    "morosidade processos judiciais impacto empresas",
    "análise crédito riscos jurídicos"
]

# ----------------------------------------------------------------------------
# 3. CASOS DE SUCESSO E BENCHMARKING
# ----------------------------------------------------------------------------
cases_sucesso = [
    f"legal tech success stories Brazil {ano_atual}",
    "automação jurídica resultados",
    "ROI tecnologia jurídica",
    "cases automação departamento jurídico",
    "transformação digital escritórios advocacia exemplos",
    f"empresas legal tech Brasil cases {ano_atual}",
    "resultados IA jurídica cases",
    "economia tempo tecnologia jurídica exemplos",
    "due diligence automatizada resultados",
    "benchmarking advogados tecnologia"
]

# ----------------------------------------------------------------------------
# 4. EDUCAÇÃO E CONCEITOS (PARA BLOG POSTS)
# ----------------------------------------------------------------------------
educacao_conceitos = [
    "o que é jurimetria",
    "como funciona análise preditiva processos",
    "KYC jurídico explicação",
    "due diligence judicial importância",
    "API dados judiciais benefícios",
    "background check jurídico como fazer",
    "dados judiciais estruturados conceito",
    "análise risco jurídico metodologia",
    "compliance jurídico guia completo",
    "inteligência artificial direito como funciona",
    "machine learning processos judiciais explicação",
    "provisionamento contingências jurídicas método"
]

# ----------------------------------------------------------------------------
# 5. COMPARATIVOS E MERCADO
# ----------------------------------------------------------------------------
comparativos_mercado = [
    f"legal tech Brazil market size {ano_atual}",
    "concorrentes análise dados judiciais",
    "soluções consulta processos judiciais",
    "plataformas jurimetria Brasil",
    "comparação ferramentas legal tech",
    f"mercado legal tech Brasil estatísticas {ano_atual}",
    "players legal tech Brasil ranking",
    "investimentos legal tech Brasil",
    "valorização mercado legal tech",
    "crescimento setor legal tech números"
]

# ----------------------------------------------------------------------------
# 6. REGULAMENTAÇÃO E COMPLIANCE
# ----------------------------------------------------------------------------
regulamentacao_compliance = [
    "LGPD dados judiciais",
    "regulamentação legal tech Brasil",
    "compliance acesso dados públicos",
    "privacidade consultas processos judiciais",
    f"novas regulamentações legal tech {ano_atual}",
    "transparência dados judiciais legislação",
    "segurança dados jurídicos compliance",
    "LGPD departamento jurídico implicações",
    "ética uso dados judiciais",
    "proteção dados processos judiciais"
]

# ----------------------------------------------------------------------------
# 7. SETORES ESPECÍFICOS (PARA SEGMENTAÇÃO)
# ----------------------------------------------------------------------------
setores_especificos = [
    "legal tech instituições financeiras",
    "automação jurídica bancos",
    "análise risco crédito dados judiciais",
    "compliance jurídico fintechs",
    "background check RH empresas",
    "due diligence M&A tecnologia",
    "gestão riscos seguradoras dados judiciais",
    "compliance corporativo ferramentas",
    "análise fornecedores risco jurídico",
    "KYC instituições financeiras processos"
]

# ----------------------------------------------------------------------------
# 8. INOVAÇÃO E FUTURO
# ----------------------------------------------------------------------------
inovacao_futuro = [
    f"futuro advocacia tecnologia {ano_atual}",
    "inteligência artificial tribunais Brasil",
    "machine learning processos judiciais",
    f"automação jurídica futuro {ano_atual + 1}",
    "digitalização judiciário brasileiro",
    f"tendências legal tech {ano_atual + 1}",
    "blockchain processos judiciais aplicações",
    "previsão futuro mercado jurídico",
    "tecnologias emergentes direito",
    "transformação digital justiça brasileira"
]

# ----------------------------------------------------------------------------
# 9. ESTATÍSTICAS E NÚMEROS (PARA INFOGRÁFICOS)
# ----------------------------------------------------------------------------
estatisticas_numeros = [
    f"estatísticas processos judiciais Brasil {ano_atual}",
    f"números judiciário brasileiro {ano_atual}",
    "tempo médio processos tribunais",
    f"volume processos CNJ estatísticas {ano_atual}",
    f"dados judiciário brasileiro {ano_atual}",
    "estatísticas litígio empresas Brasil",
    "números advocacia Brasil CNJ",
    "custos médios processos judiciais",
    "taxa congestionamento judiciário brasileiro",
    "processos trabalhistas estatísticas Brasil"
]

# ----------------------------------------------------------------------------
# 10. PAIN POINTS ESPECÍFICOS POR PRODUTO
# ----------------------------------------------------------------------------

# Para Análise de Crédito e Risco
analise_credito_risco = [
    "fraudes análise crédito prevenção",
    "background check financeiro importância",
    "KYC análise crédito melhores práticas",
    "verificação cadastral empresas métodos",
    "análise risco fornecedores dados judiciais",
    "due diligence financeira processos",
    "crédito empresarial análise risco jurídico",
    "inadimplência processos judiciais correlação"
]

# Para Predictus Jurimetria
jurimetria_preditiva = [
    "previsão resultado processos judiciais",
    "análise preditiva vantagens advocacia",
    f"jurimetria aplicações {ano_atual}",
    "IA previsão desfechos processos",
    "estatística processos judiciais métodos",
    "machine learning previsão jurídica",
    "análise probabilística processos",
    "estratégia processual dados estatísticos"
]

# Para Benchmarking de Advogados
benchmarking_advogados = [
    "como escolher advogado análise dados",
    "performance advogados métricas",
    "avaliação escritórios advocacia critérios",
    "ranking advogados dados processos",
    "análise carteira advogados métodos",
    "seleção advogados KPIs jurídicos",
    "comparação advogados desempenho processos",
    "métricas sucesso advogados dados"
]

# Para Due Diligence
due_diligence = [
    "due diligence jurídica M&A",
    "verificação processos judiciais empresas",
    "análise contingências jurídicas método",
    "due diligence fornecedores checklist",
    "investigação jurídica parcerias empresariais",
    "riscos jurídicos fusões aquisições",
    "auditoria jurídica empresas processos",
    "verificação passivo judicial empresas"
]

# Para Compliance e Monitoramento
compliance_monitoramento = [
    "monitoramento processos judiciais automatizado",
    "compliance jurídico ferramentas automação",
    "alertas processos judiciais tempo real",
    "gestão contingências jurídicas automação",
    "acompanhamento processos empresas tecnologia",
    "compliance corporativo legal tech",
    "auditoria contínua riscos jurídicos",
    "monitoramento reputacional processos judiciais"
]

# ----------------------------------------------------------------------------
# 11. NOTÍCIAS E EVENTOS RECENTES (COM DATA ATUAL)
# ----------------------------------------------------------------------------
noticias_eventos = [
    f"notícias legal tech Brasil {data_formatada}",
    f"eventos legal tech {mes_atual}/{ano_atual}",
    f"lançamentos legal tech Brasil {ano_atual}",
    f"investimentos legal tech Brasil {ano_atual}",
    f"startups legal tech Brasil {ano_atual}",
    f"AB2L novidades {ano_atual}",
    f"CNJ tecnologia {ano_atual}",
    f"inovação tribunais Brasil {ano_atual}"
]

# ----------------------------------------------------------------------------
# 12. CONTEÚDO VIRAL E TRENDING TOPICS
# ----------------------------------------------------------------------------
viral_trending = [
    f"legal tech viral {ano_atual}",
    "casos judiciais repercussão tecnologia",
    "polêmica uso IA direito",
    "debates legal tech Brasil",
    "controvérsias automação jurídica",
    "discussões futuro advocacia",
    "opiniões especialistas legal tech"
]

# ============================================================================
# QUERY ESPECIAL: COMBINAÇÕES PARA PESQUISAS MAIS ESPECÍFICAS
# ============================================================================
queries_combinadas = (
    tendencias_mercado
    + dores_desafios
    + cases_sucesso
    + educacao_conceitos
    + comparativos_mercado
    + regulamentacao_compliance
    + setores_especificos
    + inovacao_futuro
    + estatisticas_numeros
    + analise_credito_risco
    + jurimetria_preditiva
    + benchmarking_advogados
    + due_diligence
    + compliance_monitoramento
    + noticias_eventos
    + viral_trending
)

# ============================================================================
# DICIONÁRIO COMPLETO COM TODAS AS QUERIES ORGANIZADAS
# ============================================================================
todas_queries = {
    "tendencias_mercado": tendencias_mercado,
    "dores_desafios": dores_desafios,
    "cases_sucesso": cases_sucesso,
    "educacao_conceitos": educacao_conceitos,
    "comparativos_mercado": comparativos_mercado,
    "regulamentacao_compliance": regulamentacao_compliance,
    "setores_especificos": setores_especificos,
    "inovacao_futuro": inovacao_futuro,
    "estatisticas_numeros": estatisticas_numeros,
    "analise_credito_risco": analise_credito_risco,
    "jurimetria_preditiva": jurimetria_preditiva,
    "benchmarking_advogados": benchmarking_advogados,
    "due_diligence": due_diligence,
    "compliance_monitoramento": compliance_monitoramento,
    "noticias_eventos": noticias_eventos,
    "viral_trending": viral_trending,
    "queries_combinadas": queries_combinadas
}

# ============================================================================
# FUNÇÃO PARA EXIBIR QUERIES POR CATEGORIA
# ============================================================================
def exibir_queries_por_categoria(categoria):
    """
    Exibe as queries de uma categoria específica
    
    Args:
        categoria (str): Nome da categoria desejada
    """
    if categoria in todas_queries:
        print(f"\n{'='*80}")
        print(f"CATEGORIA: {categoria.upper().replace('_', ' ')}")
        print(f"{'='*80}")
        for i, query in enumerate(todas_queries[categoria], 1):
            print(f"{i:2d}. {query}")
    else:
        print(f"Categoria '{categoria}' não encontrada!")
        print(f"Categorias disponíveis: {', '.join(todas_queries.keys())}")

# ============================================================================
# FUNÇÃO PARA OBTER TODAS AS QUERIES EM UMA LISTA
# ============================================================================
def obter_todas_queries():
    """
    Retorna uma lista única com todas as queries
    
    Returns:
        list: Lista com todas as queries de todas as categorias
    """
    todas = []
    for queries in todas_queries.values():
        todas.extend(queries)
    return todas

# ============================================================================
# FUNÇÃO PARA EXPORTAR QUERIES PARA ARQUIVO
# ============================================================================
def exportar_queries(nome_arquivo="queries_tavily.txt"):
    """
    Exporta todas as queries para um arquivo de texto
    
    Args:
        nome_arquivo (str): Nome do arquivo para salvar
    """
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        f.write(f"QUERIES TAVILY - PREDICTUS MARKETING\n")
        f.write(f"Gerado em: {data_formatada}\n")
        f.write(f"{'='*80}\n\n")
        
        for categoria, queries in todas_queries.items():
            f.write(f"\n{'='*80}\n")
            f.write(f"{categoria.upper().replace('_', ' ')}\n")
            f.write(f"{'='*80}\n")
            for i, query in enumerate(queries, 1):
                f.write(f"{i:2d}. {query}\n")
    
    print(f"Queries exportadas para: {nome_arquivo}")

# ============================================================================
# EXEMPLO DE USO
# ============================================================================
if __name__ == "__main__":
    # Exibir informações gerais
    print(f"Data atual: {data_formatada}")
    print(f"Ano: {ano_atual}")
    print(f"Total de categorias: {len(todas_queries)}")
    print(f"Total de queries: {len(obter_todas_queries())}")
    
    # Exemplo: exibir queries de uma categoria específica
    print("\n" + "="*80)
    print("EXEMPLO: Queries para Tendências de Mercado")
    print("="*80)
    exibir_queries_por_categoria("tendencias_mercado")
    
    # Exemplo: listar todas as categorias disponíveis
    print("\n" + "="*80)
    print("CATEGORIAS DISPONÍVEIS:")
    print("="*80)
    for i, categoria in enumerate(todas_queries.keys(), 1):
        total = len(todas_queries[categoria])
        print(f"{i:2d}. {categoria.replace('_', ' ').title()} ({total} queries)")
    
    # Descomente a linha abaixo para exportar as queries para arquivo
    # exportar_queries()