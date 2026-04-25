class ShortenerBaseError(Exception):
    pass


class LongUrlNotFoundError(ShortenerBaseError):
    pass


class SlugAlreadyExistsError(ShortenerBaseError):
    pass


class RedisCacheError(ShortenerBaseError):
    pass
