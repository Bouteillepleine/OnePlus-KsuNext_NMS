import hashlib
import struct
import sys

APK_SIG_BLOCK_MAGIC = b"APK Sig Block 42"
V2_BLOCK_ID = 0x7109871A
V3_BLOCK_ID = 0xF05368C0


def find_central_directory_offset(blob):
    tail = blob[-(65536 + 22):]
    pos = tail.rfind(b"PK\x05\x06")
    if pos < 0:
        raise ValueError("no end-of-central-directory record")
    eocd = len(blob) - len(tail) + pos
    return struct.unpack_from("<I", blob, eocd + 16)[0]


def find_signing_block(blob):
    cd = find_central_directory_offset(blob)
    if cd < 32 or blob[cd - 16:cd] != APK_SIG_BLOCK_MAGIC:
        raise ValueError("no APK signing block")
    size = struct.unpack_from("<Q", blob, cd - 24)[0]
    start = cd - size - 8
    if start < 0 or struct.unpack_from("<Q", blob, start)[0] != size:
        raise ValueError("APK signing block size fields disagree")
    return start + 8, cd - 24


def iter_id_value_pairs(blob, start, end):
    pos = start
    while pos + 12 <= end:
        length = struct.unpack_from("<Q", blob, pos)[0]
        if length < 4 or pos + 8 + length > end:
            raise ValueError("truncated id-value pair")
        block_id = struct.unpack_from("<I", blob, pos + 8)[0]
        yield block_id, pos + 12, pos + 8 + length
        pos += 8 + length


def read_length_prefixed(blob, pos, end):
    if pos + 4 > end:
        raise ValueError("truncated length prefix")
    length = struct.unpack_from("<I", blob, pos)[0]
    if pos + 4 + length > end:
        raise ValueError("length prefix overruns its container")
    return pos + 4, pos + 4 + length


def first_certificate(blob, start, end):
    signers_pos, signers_end = read_length_prefixed(blob, start, end)
    signer_pos, signer_end = read_length_prefixed(blob, signers_pos, signers_end)
    signed_pos, signed_end = read_length_prefixed(blob, signer_pos, signer_end)
    digests_pos, digests_end = read_length_prefixed(blob, signed_pos, signed_end)
    certs_pos, certs_end = read_length_prefixed(blob, digests_end, signed_end)
    cert_pos, cert_end = read_length_prefixed(blob, certs_pos, certs_end)
    return blob[cert_pos:cert_end]


def signer_digest(path):
    with open(path, "rb") as fh:
        blob = fh.read()
    start, end = find_signing_block(blob)
    found = {}
    for block_id, value_start, value_end in iter_id_value_pairs(blob, start, end):
        if block_id in (V2_BLOCK_ID, V3_BLOCK_ID):
            found[block_id] = first_certificate(blob, value_start, value_end)
    cert = found.get(V2_BLOCK_ID) or found.get(V3_BLOCK_ID)
    if cert is None:
        raise ValueError("no v2 or v3 signature block")
    return hashlib.sha256(cert).hexdigest(), len(cert)


def main(argv):
    if len(argv) < 2:
        print("usage: apk_signer_digest.py <apk> [expected_sha256]", file=sys.stderr)
        return 2
    try:
        digest, size = signer_digest(argv[1])
    except (OSError, ValueError, struct.error) as exc:
        print("error: %s: %s" % (argv[1], exc), file=sys.stderr)
        return 1
    print("%s %d" % (digest, size))
    if len(argv) > 2 and argv[2].lower() != digest:
        print("error: %s signer is %s, expected %s" % (argv[1], digest, argv[2].lower()),
              file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
