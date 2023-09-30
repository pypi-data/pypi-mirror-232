# Copyright (C) 2022-2023 AyiinXd <https://github.com/AyiinXd>

# This file is part of GeneratorPassword.

# GeneratorPassword is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# GeneratorPassword is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with GeneratorPassword.  If not, see <http://www.gnu.org/licenses/>.

import string

from random import choice
from typing import Dict, Optional, Union

from generator.exception import LengthNeeded
from generator.storage import Storage
from generator.utils import sha256


class Generator(Storage):
    def __init__(self):
        self._dict: Optional[Dict] = {}
        self._string = string.ascii_letters
        self._space = '-_='
        self._name: str = 'GP'
        self.conn = self.get_conn()

    def password(
        self,
        user_id: int,
        name: str = None,
        length: Union[int, str] = None
    ):
        if name:
            self.name = name + self._space
        else:
            self.name = self._name + self._space
        if not length:
            raise LengthNeeded()
        passwd = self.name + ''.join(choice(self._string) for _ in range(int(length)))
        random_id = ''.join(choice(string.digits) for _ in range(8))
        self.add_password(user_id=user_id, key=passwd, random_id=random_id)
        return passwd

    def password_sha256(
        self,
        user_id: int,
        name: str = None,
        length: Union[int, str] = None
    ):
        if name:
            self.name = name + self._space
        else:
            self.name = self._name + self._space
        if not length:
            raise LengthNeeded()
        passwd = self.name + ''.join(choice(self._string) for _ in range(int(length)))
        return sha256(passwd)
