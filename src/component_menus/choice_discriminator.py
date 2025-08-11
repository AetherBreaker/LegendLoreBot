if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from collections.abc import Sequence
from logging import getLogger

from disnake import ApplicationCommandInteraction, ButtonStyle, MessageInteraction, SelectOption
from disnake.ui import Button, StringSelect, View, button, string_select

logger = getLogger(__name__)


class DiscriminateChoices(View):
  """
  A class that will handle the creation and sending of a component menu for discriminating a user choice that cannot be
  resolved to a single unique value.
  """

  def __init__(
    self,
    inter: ApplicationCommandInteraction,
    uid_choices: dict["CharacterUID", str],  # pyright: ignore[reportUndefinedVariable]  # noqa: F821
    *args,
    submit_button: bool = True,
    **kwargs,
  ):
    self._root_interaction = inter

    self._choices = uid_choices

    self.add_item(
      CharacterUIDSelector(
        options=self._choices,
      )
    )

    if submit_button:
      self.add_item(
        SubmitButton(
          label="Submit",
          style=ButtonStyle.success,
        )
      )

    super().__init__(*args, **kwargs)

  @string_select(placeholder="Select a character UID...", row=0)
  async def select_character(self, select: StringSelect, inter: MessageInteraction): ...

  @button(label="Submit", style=ButtonStyle.success, disabled=True, row=1)
  async def submit(self, button: Button, inter: MessageInteraction): ...

  async def send_self(self):
    await self._root_interaction.send("Please select an option:", view=self)


class CharacterUIDSelector(StringSelect):
  async def callback(self, inter: MessageInteraction): ...


class SubmitButton(Button):
  async def callback(self, inter: MessageInteraction): ...
