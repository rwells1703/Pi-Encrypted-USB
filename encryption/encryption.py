import os

def get_tpm_shell_env():
    # Specify the host and port for the TPM server
    env = os.environ.copy()
    env["TPM2TOOLS_TCTI"] = "mssim:host=localhost,port=2321"
    
    return env