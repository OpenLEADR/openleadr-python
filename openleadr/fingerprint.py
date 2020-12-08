from argparse import ArgumentParser
from openleadr.utils import certificate_fingerprint


def show_fingerprint():
    parser = ArgumentParser()
    parser.add_argument('certificate', type=str)
    args = parser.parse_args()

    if 'certificate' in args:
        with open(args.certificate) as file:
            cert_str = file.read()
            print(certificate_fingerprint(cert_str))
