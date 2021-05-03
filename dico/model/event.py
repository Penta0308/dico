import datetime
from .channel import Channel, Message
from .emoji import Emoji
from .guild import Guild, Member
from .permission import Role
from .snowflake import Snowflake
from .user import User
from ..base.model import EventBase


class Ready(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.v = resp["v"]
        self.user = User.create(client, resp["user"])
        self.guilds = resp["guilds"]
        self.session_id = resp["session_id"]
        self.shard = resp.get("shard", [])
        self.application = resp["application"]


class ApplicationCommandCreate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)


class ApplicationCommandUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)


class ApplicationCommandDelete(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)


ChannelCreate = Channel


class ChannelUpdate(Channel):
    def __del__(self):
        Channel.create(self.client, self.raw)

    @classmethod
    def create(cls, client, resp, **kwargs):
        return cls(client, resp, **kwargs)

    @property
    def original(self):
        return self.client.get_channel(self.id)


class ChannelDelete(Channel):
    def __del__(self):
        self.client.cache.remove(self.id, self._cache_type)


class ChannelPinsUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake.optional(resp.get("guild_id"))
        self.channel_id = Snowflake(resp["channel_id"])
        self.__last_pin_timestamp = resp.get("last_pin_timestamp")
        self.last_pin_timestamp = datetime.datetime.fromisoformat(self.__last_pin_timestamp) if self.__last_pin_timestamp else self.__last_pin_timestamp

    @property
    def channel(self):
        return self.client.get_channel(self.channel_id)

    @property
    def guild(self):
        if self.guild_id:
            return self.client.get_guild(self.guild_id)


GuildCreate = Guild
GuildUpdate = Guild
GuildDelete = Guild


class GuildBanAdd(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.user = User.create(self.client, resp["user"])

    @property
    def guild(self):
        return self.client.cache.get_guild(self.guild_id)


class GuildBanRemove(GuildBanAdd):
    pass


class GuildEmojisUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.emojis = [Emoji(self.client, x) for x in resp["emojis"]]

    @property
    def guild(self):
        return self.client.cache.get_guild(self.guild_id)


class GuildIntegrationsUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])

    @property
    def guild(self):
        return self.client.cache.get_guild(self.guild_id)


GuildMemberAdd = Member


class GuildMemberRemove(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.user = User.create(self.client, resp["user"])

    @property
    def guild(self):
        return self.client.cache.get_guild(self.guild_id)


class GuildRoleCreate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.role = Role.create(client, resp["role"], guild_id=self.guild_id)

    @property
    def guild(self):
        return self.client.get_guild(self.guild_id)


class GuildRoleUpdate(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.role = Role(client, resp["role"], guild_id=self.guild_id)

    def __del__(self):
        Role.create(self.client, self.raw["role"], guild_id=self.guild_id)

    @property
    def guild(self):
        return self.client.get_guild(self.guild_id)

    @property
    def original(self):
        return self.client.get(self.role.id)


class GuildRoleDelete(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.guild_id = Snowflake(resp["guild_id"])
        self.role_id = Snowflake(resp["role_id"])

    def __del__(self):
        self.client.cache.remove(self.role_id, "role")

    @property
    def guild(self):
        return self.client.get_guild(self.guild_id)

    @property
    def role(self):
        return self.guild.get_role(self.role_id)


MessageCreate = Message


class MessageUpdate(Message):
    def __del__(self):
        Message.create(self.client, self.raw)

    @classmethod
    def create(cls, client, resp, **kwargs):
        return cls(client, resp, **kwargs)

    @property
    def original(self):
        return self.client.get(self.id)


class MessageDelete(EventBase):
    def __init__(self, client, resp: dict):
        super().__init__(client, resp)
        self.id = Snowflake(resp["id"])
        self.channel_id = Snowflake(resp["channel_id"])
        self.guild_id = Snowflake.optional(resp.get("guild_id"))

    def __del__(self):
        self.client.cache.remove(self.id, "message")

    @property
    def message(self):
        return self.client.get(self.id)

    @property
    def channel(self):
        return self.client.get_channel(self.channel_id)

    @property
    def guild(self):
        if self.guild_id:
            return self.client.get_guild(self.guild_id)
