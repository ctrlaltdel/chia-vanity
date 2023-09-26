# ./.venv/bin/python

import sys
from secrets import token_bytes

from blspy import AugSchemeMPL

from chia.util.keychain import mnemonic_to_seed, bytes_to_mnemonic
from chia.util.bech32m import encode_puzzle_hash
from chia.consensus.coinbase import create_puzzlehash_for_pk
from chia.util.ints import uint32

from multiprocessing import Pool, cpu_count

from chia.wallet.derive_keys import master_sk_to_wallet_sk_unhardened

# Base32 alphabet
#
#  	    0	1	2	3	4	5	6	7
# +0	q	p	z	r	y	9	x	8
# +8	g	f	2	t	v	d	w	0
# +16	s	3	j	n	5	4	k	h
# +24	c	e	6	m	u	a	7	l
#
# 0 2 3 4 5 6 7 8 9 a c d e f g h j k l m n p q r s t u v w x y z

BASE32_ALPHABET = "023456789acdefghjklmnpqrstuvwxyz"
ADDRESS_PREFIX = "xch"


def task(word):
    while True:
        entropy = token_bytes(32)

        mnemonic = bytes_to_mnemonic(entropy)

        seed = mnemonic_to_seed(mnemonic)

        master_sk = AugSchemeMPL.key_gen(seed)

        wallet_sk = master_sk_to_wallet_sk_unhardened(master_sk, uint32(0))

        wallet_address = encode_puzzle_hash(
            create_puzzlehash_for_pk(wallet_sk.get_g1()), ADDRESS_PREFIX
        )

        if word in wallet_address:
            print(word)
            return (wallet_address, mnemonic, repr(master_sk))


if __name__ == "__main__":
    word = sys.argv[1]

    for c in word:
        if c not in BASE32_ALPHABET:
            raise Exception(f"Character {c} from {word} is not in base32 alphabet")

    print(task(word))

    # with Pool() as p:
    #     results = []

    #     for i in range(cpu_count()):
    #         results.append(p.apply_async(task, (word,)))

    #     while True:
    #         for res in results:
    #             if res.ready():
    #                 print(res)
    #                 wallet_address, mnemonic, master_sk = res.get()
    #                 print(wallet_address, mnemonic, master_sk)
    #                 sys.exit(0)
