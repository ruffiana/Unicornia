from typing import Optional
from redbot.core.utils.predicates import MessagePredicate
from redbot.core import commands
import discord


class CustomMessagePredicate(MessagePredicate):
    """
    CustomMessagePredicate is a subclass of redbot.core.utils.predicates.MessagePredicate
    that provides extended options for yes/no responses.

    Methods:
    yes_or_no: Overwrites base class method. Match if the message is a form of 'yes' or
    'no'. This will also assign `True` for *yes*, or `False` for *no* to the `result`
    class attribute.
    """

    POSITIVES = ["yes", "y", "yup", "yeah"]
    NEGATIVES = ["no", "n", "nope", "nah"]

    def __init__(self):
        super().__init__()

    def yes_or_no(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.abc.Messageable] = None,
        user: Optional[discord.abc.User] = None,
    ) -> "MessagePredicate":
        """Match if the message is a form of 'yes' or 'no'.

        This will assign ``True`` for *yes*, or ``False`` for *no* to
        the `result` attribute.

        Parameters
        ----------
        ctx : Optional[Context]
            Same as ``ctx`` in :meth:`same_context`.
        channel : Optional[discord.abc.Messageable]
            Same as ``channel`` in :meth:`same_context`.
        user : Optional[discord.abc.User]
            Same as ``user`` in :meth:`same_context`.

        Returns
        -------
        MessagePredicate
            The event predicate.

        """
        same_context = MessagePredicate.same_context(ctx, channel, user)

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False
            content = m.content.lower()
            if content in cls.POSITIVES:
                self.result = True
            elif content in cls.NEGATIVES:
                self.result = False
            else:
                return False
            return True

        return cls(predicate)
