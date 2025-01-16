from abc import ABC, abstractmethod

import discord


class TextResponder(ABC):
    ignore_case = True
    delete_after = None
    pattern = ""

    @abstractmethod
    async def response(self, message: discord.Message, matched_text: str):
        """Define the response to the matched message"""
        pass

    def __str__(self):
        return f"{self.__class__.__name__}(pattern={self.pattern})"

    def __repr__(self):
        return f"<{self.__class__.__name__} pattern={self.pattern}>"
