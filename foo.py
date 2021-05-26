import binascii

from typos import Typos

from bip_utils import (
    Bip32,
    Bip39WordsNum,
    # Bip49,
    # Bip84,
    Bip32Utils,
    Bip39MnemonicGenerator,
    Bip39MnemonicValidator,
    Bip39SeedGenerator,
)


class Wallet(object):
    def __init__(self, mnemonic=None, passphrase=None):
        mnemonic = mnemonic or Bip39MnemonicGenerator().FromWordsNumber(
            Bip39WordsNum.WORDS_NUM_24
        )
        Bip39MnemonicValidator(mnemonic).Validate()
        self.mnemonic = mnemonic
        self.passphrase = passphrase or ""

    def seed_bytes(self, passphrase=None):
        passphrase = passphrase or self.passphrase
        return Bip39SeedGenerator(self.mnemonic).Generate(passphrase)

    def master(self, passphrase=None):
        passphrase = passphrase or self.passphrase
        return Bip32.FromSeed(self.seed_bytes(passphrase))

    def fingerprint(self, passphrase=None):
        passphrase = passphrase or self.passphrase
        return self.master(passphrase).FingerPrint()


class PassphraseChecker(object):
    def __init__(self, wallet, predicate):
        self.wallet = wallet
        self.predicate = predicate

    def __call__(self, passphrase):
        return self.predicate(self.wallet.fingerprint(passphrase))


class FingerprintChecker(object):
    def __init__(self, target_fingerprint):
        self.target_fingerprint = binascii.unhexlify(target_fingerprint)

    def __call__(self, fingerprint):
        return fingerprint == self.target_fingerprint


def guess_all(inputs, predicate):
    # Make multiproc/GPU accelerated/distributed
    for input in inputs:
        if predicate(input): return input

# https://iancoleman.io/bip39/
mnemonic = "chase wonder voice rack custom sport fix decline body hollow wreck stay dress resist space solid gospel pumpkin shoot tank cable dignity own pigeon"
target_fingerprint = b"6aa00e9a"
best_guess = "hysterichorsebatterystaple"

wallet = Wallet(mnemonic)
make_attempt = PassphraseChecker(wallet, FingerprintChecker(target_fingerprint))

# Try using a b+-tree/sqlite/pandas dataframe
typos = Typos(best_guess, max_edit_distance=2)

if __name__ == "__main__":
    print(guess_all(typos, make_attempt))
