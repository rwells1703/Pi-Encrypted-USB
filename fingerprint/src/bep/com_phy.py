#!/usr/bin/env python3

# Copyright (c) 2020 Fingerprint Cards AB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""PHY interface wrapper functions"""
# pylint: disable = R0903


class ComPhy(object):
    """Wraps communication interface"""

    def __init__(self, interface='uart'):
        if interface == 'uart':
            from .uart import Uart
            self._comphy = Uart()
        elif interface == 'spi':
            from .fpc5832spi import Fpc5832spi
            self._comphy = Fpc5832spi()
        elif interface == 'rpispi':
            from .rpispi import Rpispi
            self._comphy = Rpispi()

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return getattr(self.attr)
        return getattr(self._comphy, attr)
