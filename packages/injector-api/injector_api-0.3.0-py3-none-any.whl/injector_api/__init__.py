from .container import DependencyContainer, SINGLETON, TRANSIENT, SCOPED, container
from .loader import inject, load_modules_from_subdirectories,configure
from .scopeMiddlware import ScopeMiddleware

__version__ = '0.2.0'