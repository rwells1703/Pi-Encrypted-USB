#!/usr/bin/env python3

from bep.bep_extended import BepExtended
from bep.com_phy import ComPhy

def main():
    interface = "rpispi"

    phy = ComPhy(interface)
    assert phy.connect(timeout=6)
    
    bep_interface = BepExtended(phy)

    run(bep_interface)

    phy.close()

def run(bep_interface):
    version = bep_interface.version_get()
    print(version)

if __name__ == "__main__":
    main()
