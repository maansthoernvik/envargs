class EnvError(Exception):
    msg = "Base err msg"

    def __init__(self, *args):
        self.msg = self.msg.format(*args)

    def __str__(self):  # pragma: no cover
        return self.msg


class RequiredError(EnvError):
    msg = "Environment variable '{}' was required but not found"


class ParseError(EnvError):
    msg = "Environment variable '{}' of type '{}' could not be parsed using " \
          "value '{}'"
