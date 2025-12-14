import time
import functools
import inspect
import logging


logger = logging.getLogger(__name__)

def measure_execution_time(func):
    """
    Decorador para medir o tempo de execução de funções Síncronas e Assíncronas.
    """
    
    # Verifica se a função original é assíncrona (corrotina)
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                logger.info(f"⏱️  [ASYNC] {func.__name__} executou em {elapsed:.4f} segundos")
        return wrapper
    else:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                end_time = time.perf_counter()
                elapsed = end_time - start_time
                logger.info(f"⏱️  [SYNC] {func.__name__} executou em {elapsed:.4f} segundos")
        return wrapper