from aiogram import Dispatcher

from loader import dp
<<<<<<< HEAD
# from .is_admin import AdminFilter


if __name__ == "filters":
    #dp.filters_factory.bind(is_admin)
    pass
=======
from .admins import AdminFilter
from .group_chat import IsGroup
from .private_chat import IsPrivate
from .super_admin import IsSuperAdmin


if __name__ == "filters":
    dp.filters_factory.bind(AdminFilter)
    dp.filters_factory.bind(IsGroup)
    dp.filters_factory.bind(IsPrivate)
    dp.filters_factory.bind(IsSuperAdmin)
>>>>>>> master
