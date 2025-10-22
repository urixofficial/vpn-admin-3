# [file name]: infrastructure/__init__.py
# [file content begin]
"""
Инфраструктурные компоненты - VPN менеджеры, файловое хранилище и т.д.
"""

from .wireguard.wireguard_manager import wg_manager

__all__ = ["wg_manager"]
# [file content end]