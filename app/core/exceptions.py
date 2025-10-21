class VPNAdminException(Exception):
    """Базовое исключение приложения"""
    pass


class UserNotFoundException(VPNAdminException):
    """Пользователь не найден"""
    pass


class UserAlreadyExistsException(VPNAdminException):
    """Пользователь уже существует"""
    pass


class InvalidConfigurationException(VPNAdminException):
    """Неверная конфигурация"""
    pass


class VPNConfigurationException(VPNAdminException):
    """Ошибка конфигурации VPN"""
    pass


class DatabaseException(VPNAdminException):
    """Ошибка базы данных"""
    pass


class TransactionException(VPNAdminException):
    """Ошибка транзакции"""
    pass