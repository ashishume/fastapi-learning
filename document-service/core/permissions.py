from enum import Enum


class PERMISSIONS(Enum):
    READ = "read"
    WRITE = "write"
    COMMENT = "comment"


class ROLES(Enum):
    ADMIN = "admin"
    USER = "user"
    VIEWER = "viewer"
