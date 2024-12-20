from typing import Optional, Callable, Union, Iterable
from redbot.core.utils.predicates import MessagePredicate
from redbot.core import commands
import discord
from discord.ext import commands as dpy_commands


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

    def __init__(
        self, predicate: Callable[["MessagePredicate", discord.Message], bool]
    ):
        super().__init__(predicate)

    @classmethod
    def same_context(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.abc.Messageable] = None,
        users: Optional[Union[discord.abc.User, Iterable[discord.abc.User]]] = None,
    ) -> "MessagePredicate":
        """Match if the message fits the described context.

        Parameters
        ----------
        ctx : Optional[Context]
            The current invocation context.
        channel : Optional[discord.abc.Messageable]
            The messageable object we expect a message in. If unspecified,
            defaults to ``ctx.channel``. If ``ctx`` is unspecified
            too, the message's channel will be ignored.
        users : Optional[Union[discord.abc.User, Iterable[discord.abc.User]]]
            The user or users we expect a message from. If unspecified,
            defaults to ``ctx.author``. If ``ctx`` is unspecified
            too, the message's author will be ignored.

        Returns
        -------
        MessagePredicate
            The event predicate.

        """
        check_dm_channel = False
        # using dpy_commands.Context to keep the Messageable contract in full
        if isinstance(channel, dpy_commands.Context):
            channel = channel.channel
        elif isinstance(channel, (discord.User, discord.Member)):
            check_dm_channel = True

        if ctx is not None:
            channel = channel or ctx.channel
            users = users or ctx.author

        user_ids = (
            {users.id} if isinstance(users, discord.abc.User) else {u.id for u in users}
        )

        return cls(
            lambda self, m: (users is None or m.author.id in user_ids)
            and (
                channel is None
                or (
                    channel.id == m.author.id
                    and isinstance(m.channel, discord.DMChannel)
                    if check_dm_channel
                    else channel.id == m.channel.id
                )
            )
        )

    @classmethod
    def yes_or_no(
        cls,
        ctx: Optional[commands.Context] = None,
        channel: Optional[discord.abc.Messageable] = None,
        users: Optional[Union[discord.abc.User, Iterable[discord.abc.User]]] = None,
    ) -> "CustomMessagePredicate":
        """Match if the message is a form of 'yes' or 'no'.

        This will assign ``True`` for *yes*, or ``False`` for *no* to
        the `result` attribute.

        Parameters
        ----------
        ctx : Optional[Context]
            Same as ``ctx`` in :meth:`same_context`.
        channel : Optional[discord.abc.Messageable]
            Same as ``channel`` in :meth:`same_context`.
        users : Optional[Union[discord.abc.User, Iterable[discord.abc.User]]]
            Same as ``user`` in :meth:`same_context`.

        Returns
        -------
        CustomMessagePredicate
            The event predicate.

        """
        same_context = cls.same_context(ctx, channel, users)

        def predicate(self: MessagePredicate, m: discord.Message) -> bool:
            if not same_context(m):
                return False
            content = m.content.lower()

            # added to keep track of users who have responded positively
            if not hasattr(self, "positive_responses"):
                self.positive_responses = set()

            if content in cls.POSITIVES:
                # if users is a single user, we can set the result to True
                if isinstance(users, discord.abc.User):
                    self.result = True
                # if users is a list of users, we need to keep track of who has
                # responded positively
                else:
                    self.positive_responses.add(m.author.id)
                    if len(self.positive_responses) == len(users):
                        self.result = True
            elif content in cls.NEGATIVES:
                self.result = False
            else:
                return False
            return True

        return cls(predicate)
