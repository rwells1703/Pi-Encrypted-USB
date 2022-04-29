import fingerprint.bep.com_phy

import encryption

PUBLIC_KEY = 111
PRIVATE_KEY = 222

class ComSecure(fingerprint.bep.com_phy.ComPhy):
    def __init__(self, interface):
        super().__init__(interface)