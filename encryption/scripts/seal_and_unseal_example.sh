#!/bin/bash

# TODO: Remove this, it is only useful for debug purposes
export TPM2TOOLS_TCTI=mssim:host=localhost,port=2321

# Start the TPM
tpm2_startup -c

# Create primary key of the hierarchy
echo ""
echo "- Create primary key:"
tpm2_createprimary -C o -g sha256 -G rsa -c primary.ctx

# Make primary key persistent
echo ""
echo "- Evict primary key to persitent memory:"
tpm2_evictcontrol -C o -c primary.ctx 0x81010004

# Remove the primary key context file
rm primary.ctx


# Specify the passcode used to access the key
passcode="richard"

# Hash the passcode with sha256
echo ""
echo "- Passcode hash:"
passcodehash=$(echo $passcode | tpm2_hash -g sha256 -C o --hex)
echo $passcodehash

# Extend PCR 23 with the passcode hash
tpm2_pcrextend 23:sha256=$passcodehash


# Begin a trial policy session
tpm2_startauthsession -S session.ctx

# Add a policy event based on the value of PCR number 23
echo ""
echo "- PCR Policy event (trial):"
tpm2_policypcr -S session.ctx -l sha256:23  -L policy

# Close the trial policy session
tpm2_flushcontext session.ctx

# Delete policy session context file
rm session.ctx

# Reset PCR-23, ready for unsealing
tpm2_pcrreset 23


# Generate random AES key on TPM
aeskey=$(tpm2_getrandom --hex 32)
echo ""
echo "- AES key:"
echo $aeskey

# Convert the AES key from text into a hex value
echo $aeskey | xxd -r -p -c 32 > aeskey_hex

# Flush transient objects to save memory
tpm2_flushcontext -t

tpm2_getcap handles-transient

# Create the sealing key
# then seal the AES key to it using the policy
echo ""
echo "- Create sealing key and seal AES key to it:"
tpm2_create -C 0x81010004 -L policy -i aeskey_hex -c sealing.ctx

# Make sealing key persistent
echo ""
echo "- Evict sealing key to persitent memory:"
tpm2_evictcontrol -C o -c sealing.ctx 0x81010005

# Delete policy definition file
rm policy

# Remove the file containing the AES key in hex
rm aeskey_hex

# Remove the sealing key
rm sealing.ctx








# Start the TPM
tpm2_startup -c


# Specify the passcode used to access the key
passcode="richard"

# Hash the passcode with sha256
echo ""
echo "- Passcode hash:"
passcodehash=$(echo $passcode | tpm2_hash -g sha256 -C o --hex)
echo $passcodehash

# Extend PCR 23 with the passcode hash
tpm2_pcrextend 23:sha256=$passcodehash

# Begin a real policy session
tpm2_startauthsession --policy-session -S session.ctx

# Add a policy event based on the value of PCR number 23
echo ""
echo "- PCR Policy event (real):"
tpm2_policypcr -S session.ctx -l sha256:23 -L policy

# Delete policy definition file
rm policy

# Reset PCR-23, ready for unsealing
tpm2_pcrreset 23

# Unseal the AES key from sealing key
echo ""
echo "- Unseal the AES key from sealing key:"
tpm2_unseal -psession:session.ctx -c 0x81010005 > aeskey_hex

# Close the trial policy session
tpm2_flushcontext session.ctx

# Delete policy session context file
rm session.ctx

# Read the aeskey as text from a hex file
aeskey=$(xxd -p -c 32 aeskey_hex)
echo ""
echo "AES key:"
echo $aeskey