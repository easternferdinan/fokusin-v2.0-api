import enum

class MemberRole(str, enum.Enum):
    ADMIN = 'admin'
    USER = 'user'