from disnake import Embed


class EmbedBase(Embed):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)

  def rebuild_embed(self): ...
