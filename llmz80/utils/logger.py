import logging
from termcolor import colored
from pathlib import Path
from datetime import datetime

# --- Custom Logger Formatter ---
class ConsoleFormatter(logging.Formatter):
    """Formateador personalizado para mostrar logs coloridos en consola."""
    ICONS = {
        'INFO': '🔵',
        'ERROR': '🔴',
        'WARNING': '🟡',
        'DEBUG': '🟣'
    }
    COLORS = {
        'INFO': 'cyan',
        'ERROR': 'red',
        'WARNING': 'yellow',
        'DEBUG': 'magenta'
    }

    def format(self, record: logging.LogRecord) -> str:
        icon = self.ICONS.get(record.levelname, '🔵')
        color = self.COLORS.get(record.levelname, 'white')
        message = record.getMessage()

        if record.levelname == 'INFO':
            return colored(f"{icon} {message}", color)
        return colored(f"{icon} {record.levelname}: {message}", color)

def setup_logging(log_dir: Path, log_level: str) -> None:
    """Configura el sistema de logging con handlers para archivos y consola.
    
    Args:
        log_dir: Directorio donde se guardarán los logs
        log_level: Nivel de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR')
    """
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"llmz80_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

        # Convertir string a nivel de logging
        log_level_value = getattr(logging, log_level.upper(), logging.INFO)

        # File handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ConsoleFormatter())

        # Configure root logger
        logging.basicConfig(
            level=log_level_value,
            handlers=[file_handler, console_handler],
        )
        
        # Para asegurar que funciona en todas las versiones de Python
        root_logger = logging.getLogger()
        if root_logger.hasHandlers():
            root_logger.handlers.clear()
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        root_logger.setLevel(log_level_value)

        logging.debug("Logging configurado correctamente.")
    except Exception as e:
        print(f"🔴 FATAL: Error configurando el sistema de logging: {e}")
        raise 