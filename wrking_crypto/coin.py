from Crypto.Hash import RIPEMD160

class Output():
    '''
    Represents a new UTXO locked to a specific Wallet

    Attributes
    ----------
    lock: STRING
        The corresponding Wallet (RIPEMD160 Hash of the corresponding
         puk) that this UTXO Belongs to

    amount: int
        amount of that UTXO holds

    transaction_hash: STRING
        A RIPEMD160 Hash of the Python Native Hash
    '''

    def __init__(self, lock, amount):
        self.lock = lock
        self.amount = amount
        temp_hash =  hash(self)
        self.coin_hash = RIPEMD160.new(temp_hash.to_bytes( ((temp_hash.bit_length() + 7) // 8 ) , byteorder='big') ).hexdigest()

    def __str__(self):
        return f'Owner: {self.lock.hexdigest()}\nHash: {self.coin_hash.hexdigest()}\nAmount IsCoins: {self.amount}'

    def dict(self):
        return {
            'lock':self.lock,
            'amount':self.amount,
            'coin_hash':self.coin_hash
        }

    def json(self):
        return {
            'lock':str(self.lock),
            'amount':self.amount,
            'coin_hash': self.coin_hash
        }

class Input():
    '''
    Essentially the unlocking script, including target tx's hash, the unlocking
    script, and the new owner.

    Attributes
    ----------
    hash: STRING
        RIPEMD160 hash of the previous UTXO that we own and are unlocking

    pub : STRING
        RSA Pub Key, original owners public key

    sig: Byte Array
        byte signature, signed with user prk and 'h'
    '''

    def __init__(self, hash,pub,sig):

        self.coin_hash = hash
        self.puk = pub
        self.sig = sig

    def __str__(self):
        return 'coin_hash: %s\nunlock (dict): %s' % (self.coin_hash.digest(), self.unlock)

    def dict(self):
        return {
            'coin_hash': self.coin_hash,
            'puk': self.puk,
            'sig': self.sig
        }

    def json(self):
        sig_list = []
        for byte in self.sig:
            sig_list.append(byte)

        return {
            'coin_hash': self.coin_hash,
            'puk': self.puk,
            'sig': sig_list
        }

