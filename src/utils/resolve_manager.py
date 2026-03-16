import importlib
import logging

from .resolve_connection import set_default_environment_variables


logger = logging.getLogger("davinci-resolve-mcp")


class ResolveConnection:
    def __init__(self):
        self._resolve = None
        self.logger = logger

    def connect(self):
        try:
            set_default_environment_variables()

            dvr_script = importlib.import_module("DaVinciResolveScript")

            self._resolve = dvr_script.scriptapp("Resolve")

            if self._resolve:
                self.logger.info(
                    f"Successfully connected to DaVinci Resolve: {self._resolve.GetProductName()} {self._resolve.GetVersionString()}"
                )
                return True
            self.logger.warning(
                "DaVinci Resolve is not running or scripting is not enabled."
            )
            return False
        except ImportError as e:
            self.logger.error(
                f"Failed to import DaVinciResolveScript (PYTHONPATH may be incorrect): {e}"
            )
            return False
        except Exception as e:
            self.logger.error(f"Error connecting to DaVinci Resolve: {e}")
            return False

    @property
    def instance(self):
        return self._resolve

    def is_connected(self):
        return self._resolve is not None


resolve_manager = ResolveConnection()
resolve_manager.connect()
