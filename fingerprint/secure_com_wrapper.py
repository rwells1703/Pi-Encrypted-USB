import fingerprint.bep.communication

import encryption

PUBLIC_KEY = 111
PRIVATE_KEY = 222

class ComSecure(fingerprint.bep.communication.Com):
    def __init__(self, cmd, argument=None, mtu=256):
        super().__init__(cmd, argument, mtu)