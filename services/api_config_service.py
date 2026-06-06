from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from models.api_config import ApiConfig
from schemas.api_config import ApiConfigUpdateRequest
from core.exceptions import DatabaseOperationError

def get_api_config_service(db: Session) -> ApiConfig | None:
    try:
        return db.query(ApiConfig).first()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Gagal mengambil konfigurasi API") from e

def update_api_config_service(db: Session, config_in: ApiConfigUpdateRequest) -> ApiConfig:
    try:
        config = db.query(ApiConfig).first()
        if config:
            config.api_base_url = config_in.api_base_url
            config.stress_threshold = config_in.stress_threshold
            config.stress_threshold_frequency = config_in.stress_threshold_frequency
        else:
            config = ApiConfig(
                api_base_url=config_in.api_base_url,
                stress_threshold=config_in.stress_threshold,
                stress_threshold_frequency=config_in.stress_threshold_frequency,
            )
            db.add(config)
        db.commit()
        db.refresh(config)
        return config
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Gagal memperbarui konfigurasi API") from e
