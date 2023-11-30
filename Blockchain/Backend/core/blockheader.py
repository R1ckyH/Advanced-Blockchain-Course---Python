""" 
Copyright (c) 2021 Codiesalert.com
These scripts should be used for commercial purpose without Codies Alert Permission
Any violations may lead to legal action
"""
import random
from Blockchain.Backend.core.database.database import BlockchainDB
from Blockchain.Backend.util.util import (
    hash256,
    int_to_little_endian,
    little_endian_to_int,
    int_to_little_endian,
    bits_to_target
)


class BlockHeader:
    def __init__(self, version, prevBlockHash, merkleRoot, timestamp, difficulty, nonce=None):
        self.version = version
        self.prevBlockHash = prevBlockHash
        self.merkleRoot = merkleRoot
        self.timestamp = timestamp
        self.difficulty = difficulty
        self.nonce = nonce
        self.blockHash = ""

    @classmethod
    def parse(cls, s):
        version = little_endian_to_int(s.read(4))
        prevBlockHash = s.read(32)[::-1]
        merkleRoot = s.read(32)[::-1]
        timestamp = little_endian_to_int(s.read(4))
        difficulty = s.read(4)
        nonce = s.read(4)
        return cls(version, prevBlockHash, merkleRoot, timestamp, difficulty, nonce)

    def serialize(self):
        result = int_to_little_endian(self.version, 4)
        result += self.prevBlockHash[::-1]
        result += self.merkleRoot[::-1]
        result += int_to_little_endian(self.timestamp, 4)
        result += self.difficulty
        result += self.nonce
        return result

    def to_hex(self):
        self.blockHash = self.generateBlockHash()
        self.nonce = little_endian_to_int(self.nonce)
        self.prevBlockHash = self.prevBlockHash.hex()
        self.merkleRoot = self.merkleRoot.hex()
        self.difficulty = self.difficulty.hex()

    def to_bytes(self):
        self.nonce = int_to_little_endian(self.nonce, 4)
        self.prevBlockHash = bytes.fromhex(self.prevBlockHash)
        self.merkleRoot = bytes.fromhex(self.merkleRoot)
        self.blockHash = bytes.fromhex(self.blockHash)
        self.difficulty = bytes.fromhex(self.difficulty)

    def mine(self, target, newBlockAvailable):
        self.blockHash = target + 1
        competitionOver = False
        while self.blockHash > target:
            if newBlockAvailable:
                competitionOver = True
                return competitionOver

            self.nonce = random.randint(1, 2 ** 32)
            self.blockHash = little_endian_to_int(
                hash256(
                    int_to_little_endian(self.version, 4)
                    + bytes.fromhex(self.prevBlockHash)[::-1]
                    + bytes.fromhex(self.merkleRoot)[::-1]
                    + int_to_little_endian(self.timestamp, 4)
                    + self.difficulty
                    + int_to_little_endian(self.nonce, 4)
                )
            )
            print(f"Mining Started {self.nonce}", end="\r")
        self.blockHash = int_to_little_endian(self.blockHash, 32).hex()[::-1]
        self.difficulty = self.difficulty.hex()
        return competitionOver

    def validateBlock(self):
        lastBlock = BlockchainDB().lastBlock()

        if self.prevBlockHash.hex() == lastBlock['BlockHeader']['blockHash']:
            if self.check_pow():
                return True

    def check_pow(self):
        sha = hash256(self.serialize())
        proof = little_endian_to_int(sha)
        return proof < bits_to_target(self.bits)

    def generateBlockHash(self):
        sha = hash256(self.serialize())
        proof = little_endian_to_int(sha)
        return int_to_little_endian(proof, 32).hex()[::-1]

    def to_dict(self):
        dt = self.__dict__
        return dt
