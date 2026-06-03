import enum

class MemberRole(str, enum.Enum):
    SUPERADMIN = 'superadmin'
    ADMIN = 'admin'
    MAHASISWA = 'mahasiswa'