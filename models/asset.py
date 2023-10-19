from enum import Enum
from dataclasses import dataclass

class AssetType(Enum):
    emoji = 1
    sticker = 2
    # attachment? 👀

@dataclass
class Asset:

    asset_type: AssetType
    asset_id: int
    animated: bool = False

    @property
    def url(self) -> str:
        if self.asset_type == AssetType.emoji:
            return f"https://cdn.discordapp.com/emojis/{self.asset_id}.{'gif' if self.animated else 'png'}?size=512&quality=lossless"
        elif self.asset_type == AssetType.sticker:
            return f"https://media.discordapp.net/stickers/{self.asset_id}.png?size=512"
        
        raise ValueError("Asset type not supported")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Asset):
            return NotImplemented

        return self.asset_type == other.asset_type and self.asset_id == other.asset_id