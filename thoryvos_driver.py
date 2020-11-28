"""throyvos Driver Code."""
# Importing backend libraries
import thoryvos_encoder as encoder
import thoryvos_crypto as crypto
import thoryvos_stego as stego
import thoryvos_transfer as transfer
from thoryvos_errors import *
from Crypto.Util.Padding import pad, unpad

# Importing Dependencies
from os.path import exists, splitext
from os import remove


def cleanup(*args, **kwargs):
    """Delete created files in case of error."""
    for file in args:
        if exists(file):
            remove(file)
    for file in kwargs:
        if exists(file):
            remove(file)


def get_extension(filename):
    """Return extension padded tp 8 bytes in binary format."""
    extension = splitext(filename)[1].encode()
    return pad(extension, 16)


def encryptor(infile: str, outfile: str, password: str, mode: str) -> int:
    """Encryption Driver for thoryvos backend."""
    enc = crypto.Encrypt(infile)

    if mode.upper() == 'AES':
        encrypted_data = enc.AES(password)
    elif mode.upper() == 'DES':
        encrypted_data = enc.DES(password)
    elif mode.upper() == 'SALSA20':
        encrypted_data = enc.Salsa20(password)
    else:
        raise InvalidEncryptionMode

    if not encrypted_data:
        raise EmptyDataFile

    encoder.write_data(get_extension(infile) + encrypted_data, outfile)


def decryptor(infile: str, outfile: str, password: str, mode: str) -> int:
    """Decryption Driver for thoryvos backend."""

    dec = crypto.Decrypt(infile)

    if mode.upper() == 'AES':
        decrypted_data = dec.AES(password)
    elif mode.upper() == 'DES':
        decrypted_data = dec.DES(password)
    elif mode.upper() == 'SALSA20':
        decrypted_data = dec.Salsa20(password)
    else:
        raise InvalidEncryptionMode

    if not decrypted_data:
        cleanup(outfile)
        raise EmptyDataFile

    if not outfile.endswith(dec.extension):
        outfile += dec.extension
    encoder.write_data(decrypted_data[16:], outfile)


def anon_upload(infile: str):
    """File Transfer Driver for throyvos backend."""
    if exists(infile):
        URL = transfer.upload(infile)
        return URL
    raise URLError


def anon_download(url: str):
    """File Transfer Driver for throyvos backend."""
    if transfer.verify(url):
        location = transfer.download(url)
        return location
    raise FileDoesNotExist


def verify(url: str) -> bool:
    """Check if url is valid."""
    if transfer.verify(url):
        return True
    return False


def hide_data(infile: str, outfile: str, datafile: str, lsb=None):
    """Steganography Hiding Driver for throyvos backend."""
    if not infile.endswith('.wav'):
        raise NotAWAVFile

    if not outfile.endswith('.wav'):
        raise NotAWAVFile

    try:
        lsb = int(lsb)
    except TypeError:
        lsb = None

    steganographer = stego.Stego(infile, lsb)
    lsb, datasize = steganographer.hide(datafile, outfile)

    if not datasize:
        cleanup(outfile)
        raise EmptyDataFile

    return (lsb, datasize)


def recover_data(infile: str, outfile: str, lsb: int, nbytes: int):
    """Steganography Retrieval Driver for throyvos backend."""
    if not lsb:
        raise LSBError
    if not nbytes:
        raise NBytesError

    if not infile.endswith('.wav'):
        raise NotAWAVFile

    try:
        lsb = int(lsb)
    except TypeError:
        lsb = lsb

    steganographer = stego.Stego(infile, lsb)
    if steganographer.recover(outfile, nbytes):
        return

    cleanup(outfile)
    raise UnexpectedError("Error... CleanUp...OK")


if __name__ == '__main__':
    exit("Driver code cannot be used directly.")
