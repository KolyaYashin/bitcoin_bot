from aiogram.filters import BaseFilter
from aiogram.types import Message

class IsAdmin(BaseFilter):
    admins_list: list[int] = []
    def __init__(self, admins_list):
        self.admins_list = admins_list
    async def __call__(self, message:Message):
        if message.from_user.id in self.admins_list:
            return 1
        else:
            return 0

class InPairChange(BaseFilter):
    users_dictionary: dict
    def __init__(self, users_dict):
        self.users_dictionary = users_dict
    async def __call__(self, message: Message):
        user_id = message.from_user.id
        if user_id not in self.users_dictionary:
            return 0
        else:
            if self.users_dictionary[user_id]['state'] == 'in_pair_change':
                return 1
            else:
                return 0