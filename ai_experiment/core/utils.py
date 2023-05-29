from pytz import timezone
from ai_experiment import settings

settings_time_zone = timezone(settings.TIME_ZONE)


def tz_fix(datetime_obj):
    if datetime_obj:
        return datetime_obj.astimezone(settings_time_zone)
    return datetime_obj
