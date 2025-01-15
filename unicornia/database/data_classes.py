from dataclasses import dataclass
from typing import Optional


@dataclass
class DiscordUser:
    AvatarId: str
    ClubId: Optional[int]
    CurrencyAmount: int
    DateAdded: Optional[str]
    Id: int
    IsClubAdmin: int
    NotifyOnLevelUp: int
    TotalXp: int
    UserId: int
    Username: str


@dataclass
class ShopEntry:
    AuthorId: int
    Command: Optional[str]
    DateAdded: str
    GuildConfigId: int
    Id: int
    Index: int
    Name: str
    Price: int
    RoleId: int
    RoleName: str
    RoleRequirement: Optional[str]
    Type: int


@dataclass
class ShopEntryItem:
    DateAdded: str
    Id: int
    ShopEntryId: int
    Text: str


@dataclass
class XPCurrencyReward:
    Amount: int
    DateAdded: str
    Id: int
    Level: int
    XpSettingsId: int


@dataclass
class XpRoleReward:
    DateAdded: str
    Id: int
    Level: int
    Remove: int
    RoleId: int
    XpSettingsId: int


@dataclass
class XpShopOwnedItem:
    DateAdded: str
    Id: int
    IsUsing: int
    ItemKey: str
    ItemType: int
    UserId: int


@dataclass
class BankUser:
    Balance: int
    DateAdded: Optional[str]
    Id: int
    UserId: int


@dataclass
class Club:
    DateAdded: str
    Description: Optional[str]
    Id: int
    ImageUrl: str
    Name: str
    OwnerId: int
    Xp: int
