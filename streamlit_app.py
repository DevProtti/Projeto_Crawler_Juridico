
import streamlit as st
import glob
import os
import json
import asyncio
import pandas as pd
from datetime import datetime
from app import run_pipeline, save_to_json_file

# --- Configuração da Página ---
st.set_page_config(
    page_title="Pautas Jurídicas - Predictus",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CSS Customizado para Cards e Estilo ---
st.markdown("""
<style>
    .pauta-card-content {
        height: 200px; /* Altura fixa para o conteúdo de texto */
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        overflow: hidden;
    }
    .pauta-card-content h4 {
        color: #FFFFFF;
        font-size: 1.4rem;
        font-weight: 600;
        margin-bottom: 5px;
        line-height: 1.4;
        /* Limitar titulo a 3 linhas */
        display: -webkit-box;
        -webkit-line-clamp: 3;
        -webkit-box-orient: vertical;
        overflow: hidden;
        flex-shrink: 0; /* Impede que o titulo encolha */
    }
    .pauta-card-content p {
        color: #D3D3D3;
        font-size: 1.1rem;
        margin-top: 10px;
        line-height: 1.4;
        /* O resto do espaço é para o texto, mas com limite visual */
        display: -webkit-box;
        -webkit-line-clamp: 7;
        -webkit-box-orient: vertical;
        overflow: hidden;
    }
    /* Ajuste para o botão ocupar a largura */
    .stButton button {
        width: 100%;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- Gerenciamento de Estado ---
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'grid'  # options: 'grid', 'detail'
if 'selected_pauta_index' not in st.session_state:
    st.session_state.selected_pauta_index = None
if 'selected_file' not in st.session_state:
    st.session_state.selected_file = None

# --- Funções Auxiliares ---
def load_data(filepath):
    """Carrega dados do arquivo JSON."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao ler arquivo: {e}")
        return []

def get_files():
    """Lista arquivos de saída ordenados por data."""
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    files = glob.glob(os.path.join(output_dir, "pautas_*.json"))
    return sorted(files, key=os.path.getmtime, reverse=True)

def go_to_detail(index):
    st.session_state.view_mode = 'detail'
    st.session_state.selected_pauta_index = index

def go_to_home():
    st.session_state.view_mode = 'grid'
    st.session_state.selected_pauta_index = None

def format_pauta_filename(filepath):
    """Formata o nome do arquivo para 'Pauta: dd/mm/aa'."""
    try:
        basename = os.path.basename(filepath)
        clean_name = basename.replace("pautas_predictus_", "").replace(".json", "")
        dt = datetime.strptime(clean_name, "%Y-%m-%d_%H-%M-%S")
        return dt.strftime("Pauta: %d/%m/%y")
    except:
        return os.path.basename(filepath)

# --- Sidebar ---
st.sidebar.title("⚖️ Predictus")

if st.sidebar.button("🏠 Início", use_container_width=True):
    go_to_home()

st.sidebar.markdown("---")
st.sidebar.subheader("Gerenciar Pautas")

if st.sidebar.button("🚀 Gerar Novas Pautas", use_container_width=True):
    with st.spinner("Executando crawler..."):
        try:
            new_pautas = asyncio.run(run_pipeline())
            save_to_json_file(new_pautas)
            st.success(f"{len(new_pautas)} novas pautas!")
            st.rerun() 
        except Exception as e:
            st.error(f"Erro: {e}")

st.sidebar.markdown("---")
st.sidebar.subheader("Histórico")

files = get_files()
if not files:
    st.sidebar.warning("Nenhum arquivo encontrado.")
    current_data = []
else:
    # Se nenhum arquivo selecionado, pega o mais recente
    if st.session_state.selected_file is None or st.session_state.selected_file not in files:
         st.session_state.selected_file = files[0]

    selected_file = st.sidebar.selectbox(
        "Arquivo selecionado:",
        files,
        format_func=format_pauta_filename,
        index=files.index(st.session_state.selected_file),
        key='file_selector'
    )
    
    # Atualiza o estado se mudar a seleção
    if selected_file != st.session_state.selected_file:
         st.session_state.selected_file = selected_file
         go_to_home() # Volta pra home ao trocar arquivo

    current_data = load_data(st.session_state.selected_file)

    # Navegação rápida na sidebar
    if current_data:
        st.sidebar.markdown("---")
        st.sidebar.markdown("**Navegação Rápida:**")
        for i, pauta in enumerate(current_data):
            title = pauta.get('title', pauta.get('titulo', f'Pauta {i+1}'))
            if st.sidebar.button(f"#{i+1} {title[:20]}...", key=f"nav_{i}"):
                go_to_detail(i)

# --- Área Principal ---


if st.session_state.view_mode == 'grid':
    st.title("📌 Últimas Pautas Geradas")
    
    if not current_data:
        st.info("Nenhuma pauta para exibir.")
    else:
        # Mostrar apenas as 6 primeiras ou paginação simples
        pautas_to_show = current_data[:6]
        
        # Grid layout (3 colunas)
        cols = st.columns(3)
        for i, pauta in enumerate(pautas_to_show):
            with cols[i % 3]:
                # Usando container para card effect
                with st.container(border=True):
                    # Adaptação de chaves (JSON vs Esperado)
                    titulo = pauta.get('title', pauta.get('titulo', 'Sem Título'))
                    resumo = pauta.get('hook', pauta.get('resumo', 'Sem resumo available.'))
                    
                    # Wrapper para garantir altura fixa
                    card_html = f"""
                    <div class="pauta-card-content">
                        <h4>{titulo}</h4>
                        <p>{resumo}</p>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
                    
                    if st.button("Ler mais 👉", key=f"btn_{i}"):
                        go_to_detail(i)
        
        if len(current_data) > 6:
            st.info(f"E mais {len(current_data) - 6} pautas neste arquivo. Selecione na sidebar para ver detalhes.")

elif st.session_state.view_mode == 'detail':
    idx = st.session_state.selected_pauta_index
    if idx is not None and 0 <= idx < len(current_data):
        pauta = current_data[idx]
        
        if st.button("⬅️ Voltar"):
            go_to_home()
            
        # Adaptação de chaves
        titulo = pauta.get('title', pauta.get('titulo', 'Título indisponível'))
        resumo = pauta.get('hook', pauta.get('resumo', ''))
        
        # Tratamento de bullet points
        raw_bullet_points = pauta.get('bullet_points', pauta.get('contexto', []))
        if isinstance(raw_bullet_points, list):
            contexto = "\n\n".join([f"• {bp}" for bp in raw_bullet_points])
        else:
            contexto = str(raw_bullet_points)

        # Metadados construídos a partir de campos planos
        meta = pauta.get('metadados', {})
        # Se não tiver 'metadados' explícito, monta com os campos soltos
        if not meta:
            if 'format' in pauta: meta['Formato'] = pauta['format']
            if 'predictus_product' in pauta: meta['Produto'] = pauta['predictus_product']
            if 'target_persona' in pauta: meta['Persona'] = pauta['target_persona']

        st.markdown(f"### {titulo}")
        
        # Visualização de Metadados
        if meta:
            cols_meta = st.columns(len(meta))
            for i, (k, v) in enumerate(meta.items()):
                with cols_meta[i % 4]:
                    st.markdown(f"""
                        <div style="margin-bottom: 10px;">
                            <span style="color: #888; font-size: 1.2rem;">{k}</span><br>
                            <span style="color: #FFF; font-size: 1.3rem; font-weight: bold; word-wrap: break-word; overflow-wrap: break-word;">{v}</span>
                        </div>
                    """, unsafe_allow_html=True)
            
        st.divider()
        
        col_main, col_sidebar = st.columns([3, 1])
        
        with col_main:
            st.subheader("📝 Hook / Resumo")
            st.info(resumo)
            
            st.subheader("🔍 Detalhes / Pontos Chave")
            st.markdown(contexto)
            
        with col_sidebar:
            st.subheader("🔗 Fontes")
            fontes = pauta.get('fontes', [])
            if fontes:
                for f in fontes:
                    st.markdown(f"- [Link]({f})")
            else:
                st.write("Nenhuma fonte citada.")
                
            st.markdown("---")
            st.caption("JSON Bruto")
            with st.expander("Ver JSON"):
                st.json(pauta)
    else:
        st.error("Erro ao carregar pauta. Índice inválido.")
        if st.button("Voltar"):
            go_to_home()

