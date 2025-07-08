"""
MIT License

Copyright (c) 2025 Lijing Ying <yinglj@gmail.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

@file: logger.py
@description: Configures application-wide logging with multi-process support,
              daily rotation, custom formatting, level control via
              environment/config, and a custom logger class for enhanced output.
@license: MIT
@date: 2025-04-20
"""

import logging
import sys
import os
import configparser
from typing import Optional
import logging.handlers
import gzip
import shutil

class CustomLogger(logging.Logger):
    """
    A custom logger class inheriting from logging.Logger.
    Provides enhanced 'print' and 'exception' methods that log using the
    caller's file and line number context.
    """
    def __init__(self, name: str, level: int = logging.NOTSET):
        """
        Initialize the CustomLogger.

        Args:
            name (str): The name of the logger.
            level (int): The logging level. Defaults to logging.NOTSET.
        """
        super().__init__(name, level)
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setFormatter(logging.Formatter('%(message)s'))
        self.has_console = False

    def print(self, message: str, *args, **kwargs) -> None:
        """
        Logs a message to the standard file/stream handlers AND prints to console.
        Captures and uses the caller's file name and line number in the log record.

        Args:
            message (str): The message to log and print.
            *args: Arguments to format the message string.
            **kwargs: Additional keyword arguments (not used directly by formatting).
        """
        try:
            frame = sys._getframe(2)
            filename = os.path.basename(frame.f_code.co_filename)
            lineno = frame.f_lineno
            func_name = frame.f_code.co_name
        except ValueError:
            frame = sys._getframe(1)
            filename = os.path.basename(frame.f_code.co_filename)
            lineno = frame.f_lineno
            func_name = frame.f_code.co_name

        record = self.makeRecord(
            self.name,
            logging.INFO,
            filename,
            lineno,
            message,
            args,
            None,
            func=func_name,
            sinfo=None,
        )

        if not self.has_console:
            self.addHandler(self.console_handler)
            self.has_console = True

        self.handle(record)

        self.removeHandler(self.console_handler)
        self.has_console = False

    def exception(self, msg: str, *args, exc_info=True, **kwargs) -> None:
        """
        Logs a message with level ERROR, including exception details.
        Captures the caller's file name and line number.

        Args:
            msg (str): The base message to log.
            *args: Arguments to format the message string.
            exc_info (bool | tuple): If True, grabs sys.exc_info(). Can also be an exc_info tuple.
            **kwargs: Additional keyword arguments passed to the underlying log method.
        """
        frame = sys._getframe(1)
        filename = os.path.basename(frame.f_code.co_filename)
        lineno = frame.f_lineno
        func_name = frame.f_code.co_name

        enhanced_msg = msg
        actual_exc_info = None

        if exc_info:
            actual_exc_info = sys.exc_info() if exc_info is True else exc_info
            exc_type, exc_value, _ = actual_exc_info
            if exc_type and exc_value:
                enhanced_msg = f"{msg} [error_type: {exc_type.__name__}, error_detail: {str(exc_value)}]"

        record = self.makeRecord(
            self.name,
            logging.ERROR,
            filename,
            lineno,
            enhanced_msg,
            args,
            actual_exc_info,
            func=func_name,
            sinfo=None,
        )

        self.handle(record)

def _get_log_level() -> int:
    """
    Determines the logging level based on environment variable or configuration file.

    Priority:
    1. MCP_LOG_LEVEL environment variable.
    2. 'level' setting in the [logging] section of 'mcp_config.ini'.
    3. Default to logging.INFO if neither is set or valid.

    Returns:
        int: The logging level (e.g., logging.DEBUG, logging.INFO).
    """
    log_level_str = os.getenv("MCP_LOG_LEVEL", None)
    if log_level_str:
        log_level_str = log_level_str.upper()
    else:
        try:
            config = configparser.ConfigParser()
            config_path = 'mcp_config.ini'
            if os.path.exists(config_path):
                config.read(config_path)
                log_level_str = config.get('logging', 'level', fallback='INFO').upper()
            else:
                log_level_str = 'DEBUG'
        except configparser.Error:
            print(f"Warning: Error reading log level from '{config_path}'. Defaulting to DEBUG.", file=sys.stderr)
            log_level_str = 'DEBUG'

    log_levels = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL
    }
    return log_levels.get(log_level_str, logging.INFO)

def _setup_logging():
    """
    Configures the root logger with daily rotation and gzip compression.
    """
    root_logger = logging.getLogger()
    log_level = _get_log_level()
    root_logger.setLevel(log_level)

    if root_logger.handlers:
        root_logger.handlers.clear()

    main_script = sys.argv[0] if sys.argv else "unknown_script"
    main_script_name = os.path.splitext(os.path.basename(main_script))[0]
    log_filename_base = f"logs/{main_script_name}.log"

    try:
        os.makedirs("logs", exist_ok=True)
    except OSError as e:
        print(f"Error: Failed to create logs directory 'logs': {str(e)}", file=sys.stderr)
        sys.exit(1)

    file_formatter = logging.Formatter(
        '%(asctime)s %(filename)s:%(lineno)d - %(name)s - [%(threadName)s:%(process)d] - %(levelname)s - %(message)s'
    )
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_filename_base,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding='utf-8',
        delay=True
    )
    file_handler.suffix = "%Y-%m-%d"
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(log_level)

    def compress_rotated_file(source: str, dest: str) -> None:
        with open(source, 'rb') as f_in:
            with gzip.open(dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(source)

    original_doRollover = file_handler.doRollover
    def doRollover_with_compression():
        original_doRollover()
        for f in os.listdir("logs"):
            if f.startswith(main_script_name) and f.endswith(".log") and not f.endswith(".gz"):
                source = os.path.join("logs", f)
                dest = f"{source}.gz"
                compress_rotated_file(source, dest)

    file_handler.doRollover = doRollover_with_compression

    root_logger.addHandler(file_handler)

_setup_logging()
logging.setLoggerClass(CustomLogger)
logger: CustomLogger = logging.getLogger("mcp_client")
logger.setLevel(_get_log_level())

def get_logger(name: str, level: Optional[int] = None) -> CustomLogger:
    """
    Retrieves a logger instance by name, ensuring it's of type CustomLogger.

    Args:
        name (str): The name for the logger (e.g., 'module.submodule').
        level (Optional[int]): Optional logging level to set for this specific logger.

    Returns:
        CustomLogger: An instance of the CustomLogger.
    """
    custom_logger = logging.getLogger(name)
    if level is not None:
        custom_logger.setLevel(level)
    custom_logger.propagate = True
    return custom_logger