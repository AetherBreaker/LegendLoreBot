if __name__ == "__main__":
  from logging_config import configure_logging

  configure_logging()

from logging import getLogger

from disnake import ApplicationCommandInteraction, ButtonStyle, MessageInteraction, SelectOption
from disnake.ui import Button, StringSelect, View, button, string_select
from typing_custom import CharacterUID

logger = getLogger(__name__)


class DiscriminateChoices(View):
  """
  A class that will handle the creation and sending of a component menu for discriminating a user choice that cannot be
  resolved to a single unique value.
  """

  def __init__(
    self,
    uid_choices: dict[CharacterUID, str],
    *args,
    submit_button: bool = True,
    **kwargs,
  ):
    self._choices = [SelectOption(label=name, value=str(uid)) for uid, name in uid_choices.items()]

    self.add_item(CharacterUIDSelector(view=self, options=self._choices, placeholder="Select a character UID..."))

    if submit_button:
      self.add_item(SubmitButton(view=self, label="Submit", style=ButtonStyle.success))

    super().__init__(*args, **kwargs)

  @string_select(placeholder="Select a character UID...", row=0)
  async def select_character(self, select: StringSelect, inter: MessageInteraction): ...

  @button(label="Submit", style=ButtonStyle.success, disabled=True, row=1)
  async def submit(self, button: Button, inter: MessageInteraction): ...

  async def send_self(self, inter: ApplicationCommandInteraction) -> None:
    await inter.send("Please select an option:", view=self, ephemeral=True)


class CharacterUIDSelector(StringSelect):
  def __init__(
    self,
    view: View,
    *args,
    **kwargs,
  ) -> None:
    self._view = view
    super().__init__(*args, **kwargs)

  async def callback(self, inter: MessageInteraction): ...


class SubmitButton(Button):
  def __init__(self, view: View, *args, **kwargs) -> None:
    self._view = view
    super().__init__(*args, **kwargs)

  async def callback(self, inter: MessageInteraction): ...
