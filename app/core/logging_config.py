# app/core/logging_config.py
import logging.config
import sys

def setup_logging():
    """
    Configura o sistema de logging da aplicação para usar formato JSON.
    """
    LOGGING_CONFIG = {
        "version": 1,
        "disable_existing_loggers": False, # Mantém os loggers existentes (ex: uvicorn)
        "formatters": {
            "json_formatter": {
                # Usa a classe da biblioteca python-json-logger
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                # Define os campos que você quer no seu log JSON
                "format": "%(asctime)s %(name)s %(levelname)s %(module)s %(funcName)s %(lineno)d %(message)s",
                "datefmt": "%Y-%m-%dT%H:%M:%SZ", # Formato ISO 8601 para timestamps
            },
        },
        "handlers": {
            "console_handler": {
                "class": "logging.StreamHandler",
                "stream": sys.stdout, # Envia os logs para a saída padrão
                "formatter": "json_formatter", # Usa nosso formatador JSON
            },
        },
        "loggers": {
            # Logger raiz: captura logs de todas as bibliotecas
            "": {
                "handlers": ["console_handler"],
                "level": "INFO", # Nível de log padrão
                "propagate": True,
            },
            # Logger específico para uvicorn
            "uvicorn.access": {
                "handlers": ["console_handler"],
                "level": "INFO",
                "propagate": False, # Evita duplicar logs de acesso
            },
            "uvicorn.error": {
                "handlers": ["console_handler"],
                "level": "WARNING",
                "propagate": False,
            },
        },
    }
    
    # Aplica a configuração
    logging.config.dictConfig(LOGGING_CONFIG)