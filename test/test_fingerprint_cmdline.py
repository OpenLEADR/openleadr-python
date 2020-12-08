import subprocess
from openleadr import utils
import os
import sys

def test_fingerprint_cmdline():
    cert_path = os.path.join('certificates', 'dummy_ven.crt')
    with open(cert_path) as file:
        cert_str = file.read()
    fingerprint = utils.certificate_fingerprint(cert_str)

    if sys.platform.startswith('linux') or sys.platform.startswith('darwin'):
        executable = os.path.join(sys.prefix, 'bin', 'fingerprint')
    elif sys.platform.startswith('win'):
        executable = os.path.join(sys.prefix, 'Scripts', 'fingerprint.exe')
    result = subprocess.run([executable, cert_path], stdout=subprocess.PIPE)

    assert fingerprint == result.stdout.decode('utf-8').strip()