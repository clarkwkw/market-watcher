from .translator import MessageID


class MWException(Exception):
    def __init__(
        self,
        message_id: MessageID,
        *args,
        message_args={},
        **kwargs
    ):
        self.exception_message = message_id
        self.exception_message_args = message_args


class InvalidInputException(MWException):
    pass
