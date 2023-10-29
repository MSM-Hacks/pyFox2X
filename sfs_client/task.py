import time
import threading

from pyfox2x.sfs_types import SFSObject


class SFSTask:
    result = None
    result_binary = None
    process = None
    client = None

    def __init__(self, client):
        self.client = client

    def wait_response(self, cmd, binary, deadline_delta=None):
        if deadline_delta is None:
            return self.wait_extension_response(cmd, binary)
        else:
            thread = threading.Thread(target=self.wait_extension_response, args=(cmd, binary,))
            thread.start()

            deadline = time.time() + deadline_delta
            while time.time() < deadline:
                if self.result == "fuck":
                    self.client.connection.close()
                    0 / 0
                    return SFSObject()
                if binary and self.result_binary is not None or self.result_binary is not None:
                    break
                time.sleep(1)

            del thread

            if binary and self.result_binary is not None:
                return self.result_binary
            if not binary and self.result_binary is not None:
                return self.result

            return None


    def wait_extension_response(self, command, binary):
        if binary is None:
            binary = False

        cmd, params = '', ''
        bin_packet = bytes()
        fuck_counter = 0

        while cmd != command:
            try:
                response, self.result_binary = self.client.read_response()
                #print(response)
                if self.result_binary == b"":
                    fuck_counter += 1
                else:
                    fuck_counter = 0

                if fuck_counter >= 10:
                    self.result = "fuck"
                    self.client.connection.close()
                    return

                if 'c' in response.getValue():
                    cmd, self.result = response.get("c"), response.get("p")
            except:
                continue
        #print("OK")
        if binary:
            return self.result_binary
        return self.result
