import logging
import os
from logging.handlers import RotatingFileHandler

def setup_logger(log_level=logging.INFO):
    """
    Configura o logger raiz da aplicação.
    Chame esta função APENAS UMA VEZ no ponto de entrada (app.py ou main.py).
    """
    
    # 1. Cria a pasta de logs se não existir
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 2. Define o formato (Timestamp | Nível | Arquivo | Mensagem)
    log_format = logging.Formatter(
        '%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    )

    # 3. Pega o logger raiz
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Evita duplicação de handlers se a função for chamada mais de uma vez
    if logger.hasHandlers():
        logger.handlers.clear()

    # 4. Handler de Arquivo (Com Rotação)
    # RotatingFileHandler evita que o arquivo cresça infinitamente.
    # Aqui: Máximo 5MB por arquivo, mantém os últimos 3 arquivos.
    file_handler = RotatingFileHandler(
        filename=os.path.join(log_dir, "app.log"),
        maxBytes=5*1024*1024, 
        backupCount=3,
        encoding='utf-8'
    )
    file_handler.setFormatter(log_format)
    logger.addHandler(file_handler)

    # 5. Handler de Console (Para ver no terminal enquanto desenvolve)
    # console_handler = logging.StreamHandler()
    # console_handler.setFormatter(log_format)
    # logger.addHandler(console_handler)

    # Ajusta logs de bibliotecas barulhentas para não poluir
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("openai").setLevel(logging.WARNING)

    return logger