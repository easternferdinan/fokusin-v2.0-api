import enum

class ReportRecommendationSubjectEnum(str, enum.Enum):
    DEADLINE_IS_TOMORROW_TASKS = "deadline_is_tomorrow_tasks"
    PILING_UP_TASKS = "piling_up_tasks"
    SLEEP_QUALITY = "sleep_quality"
    OTHER = "other"

class ReportRecommendationColorLabelEnum(str, enum.Enum):
    DANGER = "danger"
    WARNING = "warning"
    SUCCESS = "success"