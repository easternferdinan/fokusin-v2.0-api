import enum

class TaskCategory(str, enum.Enum):
    KULIAH = 'kuliah'
    PROYEK = 'proyek'
    LAINNYA = 'lainnya'

class TaskPriority(str, enum.Enum):
    RENDAH = 'rendah'
    SEDANG = 'sedang'
    TINGGI = 'tinggi'