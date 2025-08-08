from dependency_injector import containers, providers

from backend.core.config import configs
from backend.core.database import Database



class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        modules=[
            "backend.api.v1.endpoints.admin",
            "backend.api.v1.endpoints.auth",
            "backend.api.v1.endpoints.billing",
            "backend.api.v1.endpoints.prediction",
            "backend.core.dependencies",
        ]
    )

    db = providers.Singleton(Database, db_url=configs.DATABASE_URI)