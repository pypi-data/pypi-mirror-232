import subprocess
from k_protocol.k_protocol import get_proto_file
from create_public_proto import create_public_proto



get_proto_file("raw_proto/k_full.proto","master")
create_public_proto()

