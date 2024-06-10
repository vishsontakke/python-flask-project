from enum import Enum


LEVEL_BEGINNER      = 0
LEVEL_INTERMEDIATE  = 1
LEVEL_ADVANCE       = 2


STATUS_ACTIVE = 10
STATUS_INACTIVE = 11


levels = {
    LEVEL_BEGINNER      : 'beginner',
    LEVEL_INTERMEDIATE  : 'intermediate',
    LEVEL_ADVANCE       : 'advance'
}

level_class = {
    LEVEL_BEGINNER      : 'success',
    LEVEL_INTERMEDIATE  : 'info',
    LEVEL_ADVANCE       : 'danger'
}

statuses = {
    STATUS_ACTIVE   : 'active',
    STATUS_INACTIVE : 'inactive'
}