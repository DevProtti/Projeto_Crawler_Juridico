# src/utils/logger.py
import logging
import sys
import os
from src.config.settings import LOG_LEVEL # Vamos criar isso no passo 2

def setup_logger():
    """
    Configura o logger raiz da aplicação.
    Chame esta função apenas UMA vez no app.py.
    """
    # 1. Cria a pasta de logs se não existir
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # 2. Define o formato (Data - Nome do Modulo - Nivel - Mensagem)
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    formatter = logging.Formatter(log_format)

    # 3. Configura o Logger Raiz
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)

    # Evita duplicação de logs se a função for chamada mais de uma vez
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # 4. Handler para o Console (Terminal)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # 5. Handler para Arquivo (Salva histórico)
    file_handler = logging.FileHandler("logs/app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    logging.info("Logger inicializado com sucesso.")