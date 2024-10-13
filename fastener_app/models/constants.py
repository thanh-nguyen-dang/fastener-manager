from enum import Enum

INCH_TO_MM = 25.4
IMPERIAL_REG = r'(\d+(/\d+)?)-(\d+)'
METRIC_REG = r'M(\d+(\.\d+)?)-(\d+(\.\d+)?)'

REQUIRED_FIELDS = ['description', 'thread_size', 'material', 'finish', 'category']

class ThreadType(Enum):
    METRIC = 'metric'
    IMPERIAL = 'imperial'


class UnitType(Enum):
    MILLIMETER = 'millimeter'
    INCH = 'inch'
