import logging
import sys
from glob import glob
from pathlib import Path
from time import time

import typer
from cryptography.fernet import Fernet

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

KEY_PATH = Path(__file__).parent.joinpath("keys")

cli = typer.Typer()


@cli.command(name="create-fernet-key")
def create_fernet_key():
    key = Fernet.generate_key()
    keyfile = str(KEY_PATH.joinpath(f"{int(time())}.key"))

    with open(keyfile, "wb") as f:
        f.write(key)

    logger.info(f"Created keyfile: {keyfile}")


@cli.command(name="encrypt-file")
def encrypt_file(
    input_file: Path = typer.Argument(default=..., exists=True),
    output_file: Path = typer.Argument(default=None),
):
    keyfiles = sorted(glob(str(KEY_PATH.joinpath("*.key"))), reverse=True)
    if len(keyfiles) == 0:
        create_fernet_key()
        return encrypt_file(input_file, output_file)

    keyfile = keyfiles[0]

    logging.info(f"Encrypting with latest keyfile: {keyfile}")
    with open(keyfile, "rb") as f:
        key = Fernet(f.read())

    with open(input_file, "rb") as f:
        input_data = f.read()

    encrypted_data = key.encrypt(input_data)

    if output_file is not None:
        with open(output_file, "wb") as f:
            f.write(encrypted_data)

        logger.info(f"Encrypted file: {input_file} -> {output_file}")
    else:
        logger.info(f"Encrypted file: {input_file}:\n{encrypted_data.decode('utf-8')}")


@cli.command(name="decrypt-file")
def decrypt_file(
    input_file: Path = typer.Argument(default=..., exists=True),
    output_file: Path = typer.Argument(default=None),
):
    keyfiles = sorted(glob(str(KEY_PATH.joinpath("*.key"))))
    if len(keyfiles) == 0:
        raise Exception("No keyfiles found. Run 'create_fernet_key' first.")

    with open(input_file, "rb") as f:
        input_data = f.read()

    for keyfile in keyfiles:
        logging.info(f"Decrypting with keyfile: {keyfile}")

        with open(keyfile, "rb") as f:
            key = Fernet(f.read())

        try:
            decrypted_data = key.decrypt(input_data)
        except Exception:
            logger.info(f"Failed to decrypt with keyfile: {keyfile}")
            continue

        if output_file is not None:
            with open(output_file, "wb") as f:
                f.write(decrypted_data)

            logger.info(f"Decrypted file: {input_file} -> {output_file}")
        else:
            try:
                decrypted_data = decrypted_data.decode("utf-8")
            except UnicodeDecodeError:
                pass

            logger.info(f"Decrypted file: {input_file}:\n{decrypted_data}")

        sys.exit(0)

    logger.info(f"Unable to decrypt {input_file} with existing keys.")
    sys.exit(1)
