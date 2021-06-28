from discord.ext import commands


class OwnerOnly(commands.CheckFailure):
    """Exception raised when is_owner check is failed

    Inherits from :class:`commands.CheckFailure`
    """

    def __init__(self, message=None):
        super().__init__(message or 'Only the bot owner can use this command')


class AdminOnly(commands.CheckFailure):
    """Exception raised when is_admin check is failed

    Inherits from :class:`commands.CheckFailure`
    """

    def __init__(self, message=None):
        super().__init__(message or 'You don\'t have permission to use this command')


class WhitelistOnly(commands.CheckFailure):
    """Exception raised when is_whitelisted fails

    Inherits from :class:`commands.CheckFailure`
    """

    def __init__(self, message=None):
        super().__init__(message or "You are not whitelisted to use this command")


class TextInappropriate(commands.CheckFailure):
    """Exception raised when is_appropriate fails

    Inherits from :class:`commands.CheckFailure`
    """

    def __init__(self, message=None):
        super().__init__(message or "Input does not look appropriate")


class NoDM(commands.CheckFailure):
    """Exception raised when global DM check is failed

    Inherits from :class:`commands.CheckFailure`
    """

    def __init__(self, message=None):
        super().__init__(message or 'I don\'t accept DM commands')
