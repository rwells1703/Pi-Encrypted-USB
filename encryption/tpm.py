import subprocess
import time

import utils

class TPM:
    tpm_server_proc = None

    # Start the TPM server
    def start(self):
        # Spawn the server subprocess
        self.tpm_server_proc = subprocess.Popen(["./encryption/stpm/src/tpm_server"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        try:
            # The 1 second pause also gives the TPM server to start properly
            # TODO: Replace this long pause with checks on the output of the "startup -c" command to see if there is an error
            # if there is an error, wait and then retry till the server is ready
            stdout, stderr = self.tpm_server_proc.communicate(timeout=1)
        except subprocess.TimeoutExpired:
            # This should occur if the TPM server started properly
            # as there should be no end-of-file character yet
            pass
        else:
            # There has been an error as the TPM server has already stopped
            print("# TPM failed to start")
            utils.log(stdout)

        print("# TPM started")

    # Stop the TPM server
    def stop(self):
        # Kill the current TPM server process
        if self.tpm_server_proc:
            self.tpm_server_proc.kill()

        # Make sure any other TPM server processes are also killed (sometimes they can be left running if program crashes)
        subprocess.run("pkill -f tpm_server", shell=True)
        print("# TPM stopped")

    # Reboots the TPM server
    def restart(self):
        self.stop()
        self.start()
        
    # Reset the TPM to a blank state
    def reset(self):
        stdout = utils.execute_command(["./encryption/scripts/reset_tpm"])

        # Restart the TPM to reload the NVRAM
        self.restart()

        print("# TPM has been reset")
