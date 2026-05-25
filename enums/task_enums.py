import enum

class TaskCategory(str, enum.Enum):
    KULIAH = 'Kuliah'
    PROYEK = 'Proyek'
    LAINNYA = 'Lainnya'

class TaskPriority(str, enum.Enum):
    RENDAH = 'Rendah'
    SEDANG = 'Sedang'
    TINGGI = 'Tinggi'