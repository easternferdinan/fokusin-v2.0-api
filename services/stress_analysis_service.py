from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, UTC
import uuid
from typing import List

from core.exceptions import DatabaseOperationError
from models.stress_analysis import StressAnalysis
from schemas.stress_analysis import StressAnalysisCreateRequest
from ml.stress_predictor import get_predictor

def get_latest_stress_analysis_service(db: Session, user_id: uuid.UUID) -> StressAnalysis | None:
    """
    Retrieve the latest stress analysis for a specific user.
    """
    try:
        return db.query(StressAnalysis).filter(
            StressAnalysis.user_id == user_id
        ).order_by(StressAnalysis.created_at.desc()).first()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve latest stress analysis") from e

def create_stress_analysis_service(db: Session, data: StressAnalysisCreateRequest, user_id: uuid.UUID) -> StressAnalysis:
    """
    Perform stress analysis and save the result.
    """
    try:
        # Get the predictor and perform prediction
        predictor = get_predictor()
        stress_level = predictor.predict(data.model_dump())
        
        # Create database record
        db_analysis = StressAnalysis(
            **data.model_dump(),
            user_id=user_id,
            stress_level=stress_level
        )
        
        db.add(db_analysis)
        db.commit()
        db.refresh(db_analysis)
        return db_analysis
    except SQLAlchemyError as e:
        db.rollback()
        raise DatabaseOperationError("Failed to save stress analysis") from e
    except Exception as e:
        db.rollback()
        # Log the error if needed
        raise DatabaseOperationError(f"An unexpected error occurred during stress analysis: {str(e)}") from e

def get_all_stress_analysis_service(db: Session, user_id: uuid.UUID) -> List[StressAnalysis]:
    """
    Retrieve all stress analysis for a specific user.
    """
    try:
        return db.query(StressAnalysis).filter(
            StressAnalysis.user_id == user_id
        ).order_by(StressAnalysis.created_at.desc()).all()
    except SQLAlchemyError as e:
        raise DatabaseOperationError("Failed to retrieve stress analysis") from e