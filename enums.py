from enum import StrEnum


class GigaChatAPIScope(StrEnum):
    """GigaChat API scope. """

    PERS = "GIGACHAT_API_PERS"
    B2B = "GIGACHAT_API_B2B"
    CORP = "GIGACHAT_API_CORP"


class GigaChatModel(StrEnum):
    """Available GigaChat models. """

    GIGACHAT2 = "GigaChat-2"
    GIGACHAT2_PRO = "GigaChat-2-Pro"
    GIGACHAT2_MAX = "GigaChat-2-Max"


# Калининград: TimezoneKey.ETC_GMT_2
# Москва / Санкт-Петербург: TimezoneKey.ETC_GMT_3
# ...
# Владивосток: TimezoneKey.ETC_GMT_10
members = {f"ETC_GMT_{n}": f"Etc/GMT-{n}" for n in range(15)}
TimezoneKey = StrEnum("TimezoneKey", members)
