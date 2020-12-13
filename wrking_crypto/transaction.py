'''
Created by: Isaac Harasty

Primary Purpose: Contains the TRANSACTION, MEMLIST, and LEDGER
class for handling Verified and Unverified transactions.
'''

from wrking_crypto.user import User
from wrking_crypto.coin import Input, Output
from Crypto.Hash import RIPEMD160
from Crypto.PublicKey import RSA
from pprint import pprint
import base64


    # HOW VERIFICATION WORKS

    # Each output is LOCKED with my address...
    #
    # When I go to UNLOCK it, I present my PubKey and Signature
    # My Pubkey is hashed to verify it's coming from the key
    # that generated that address (is the owner)... THEN it's
    # used to verify my signature (that It cames from the correct owner)

class Tx():
    '''
    A class that represents a transaction, a list of inputs (unlocking scripts),
    the coins to be unlocked, and the new addresses/amounts we'll send
    the newly unlocked coins to.

    Attributes
    ----------
    unlocking_scripts: List
        List of Input objects to unlock the owned_coins object

    owned_coins: List
`       List of Output objects (coins) that will be spent in the transaction

    sent_coins: List
        list of (Address, Amount) tuples for new coins to be created from

    fee: int
        an int representing the differences in owned coins and sent coins for
        sorting in the memlist later

    reward_coin: boolean
        if a coin is a reward coin, it doesn't need to be checked for the stuff
        that normal transactions have to be

    NOTE: once a coin is added to the block chain, its 'Sent Coins' data field become
    Output objects rather than just tupples saying who we're sending the coin to
    '''

    def __init__(self, unlocking_scripts, owned_coins, sent_coins, reward_coin = False):

        self.reward_coin = reward_coin
        self.unlock = unlocking_scripts
        self.owned_coins = owned_coins
        self.sent_coins = sent_coins

        if not reward_coin:
            input_amt = 0
            for coin in owned_coins:
                input_amt += coin.amount

            output_amt = 0
            for coin in sent_coins:
                output_amt += coin[1]

            self.fee = input_amt - output_amt

        #TODO Change this hashing scheme
        self.tx_hash = self.hash()


    def check_is_valid(self):
        '''
            A helper method with series of checks to make sure the transaction
            is valid, namely

            1) the len of input blocks equals the amount of unlocking codes
            2) There exists atleast 1 desired output coin
            3) Fee isn't less than 1 (input amounts > output amounts)
            4) input tuple of self.sent_coins is the proper type and length
            5) All unlocking codes actually unlock their specific coin

            :return: false if any is false,
                     else, return true
        '''

        # Check to see if there are equal unlocking scripts to owned coins
        if len(self.unlock) != len(self.owned_coins):
            return False

        # Check to see that sent coins isnt None
        if len(self.sent_coins) == 0:
            return False

        # Make sure they're not sending more money than inputs
        if self.fee < 0:
            return False

        # Check that Sent coins are all tuples of the correct length
        for send in self.sent_coins:
            if not isinstance(send, tuple) or (len(send) != 2):
                return False

        # Check that all Unlocking Scripts can unlock each of the 'owned coins'
        all_unlockable = True
        for i in range(0, len(self.unlock)):
            all_unlockable = all_unlockable and Tx.check_Owner(self.unlock[i], self.owned_coins[i])
            if not all_unlockable:
                return False

        return True

    def check_Owner(input, output):
        '''
        A helper method to ensure that a specific input does unlock a specific output

        :param input: Input Object being checked
        :param output:  Output Object being checked
        :return: False if it fails any of the tests, else return True
        '''

        if not isinstance(input, Input) or not isinstance(output, Output):
            print("Incorrect input/output format")
            return False

        # check to see if the two are referring to the same UTXO
        if input.coin_hash != output.coin_hash:
            print("Incorrect input hash for that output")
            return False

        if User.get_wallet_from_puk(input.puk) != output.lock:
            print("Incorrect PubKey for that Wallet")
            return False

        if not User.verify_signature(input.puk, input.coin_hash, input.sig):
            print("Identity cannot be verified")
            return False

        return True

    def create_new_coins(self):
        '''
        Primary function of the Tx Class, calling this method will generate
        the correct correlating Output objects to all of the orginal inputs.

        :return: False if the transaction fails the check_is_valid() call
        :return: list of Output objects with the correct amount and lock data
        fields correlating to the self.sent_coins data field
        '''

        # Make sure this transaction is entirely valid
        if not self.reward_coin:
            if not self.check_is_valid():
                return False

        output_coin_list = []

        for new_coin in self.sent_coins:
            coin = Output(new_coin[0], new_coin[1])
            output_coin_list.append(coin)

        self.sent_coins = output_coin_list
        return output_coin_list

    def hash(self):
        temp_hash = hash(self)
        return RIPEMD160.new(temp_hash.to_bytes(((temp_hash.bit_length() + 7) // 8), byteorder='big')).hexdigest()

    def dict(self):

        unlocks = []
        locks = []
        new_coin = []
        for unl in self.unlock:
            unl_dict = unl.dict()
            unlocks.append(unl_dict)

        for loc in self.owned_coins:
            loc_dict = loc.dict()
            locks.append(loc_dict)

        for new in self.sent_coins:
            new_coin.append(list(new))


        return {
            'unlock': unlocks,
            'owned_coins': locks,
            'sent_coins': new_coin
        }

    def json(self):
        unlocks = []
        locks = []
        new_coin = []

        if self.unlock:
            for unl in self.unlock:
                unl_dict = unl.json()
                unlocks.append(unl_dict)

        if self.owned_coins:
            for loc in self.owned_coins:
                loc_dict = loc.json()
                locks.append(loc_dict)

        for new in self.sent_coins:
            new_dict = new.dict()
            new_coin.append(new_dict)

        return {
            'unlock': unlocks,
            'owned_coins': locks,
            'sent_coins': new_coin,
            'reward_coin': self.reward_coin
        }



if __name__ == '__main__':

    isaac = User()
    lily = User()

    utxos = [Output(isaac.wal, 10), Output(isaac.wal, 20), Output(isaac.wal, 5)]
    unlocks = []

    for utx in utxos:
        sig = isaac.sign(utx.coin_hash)
        unlock = Input(utx.coin_hash, isaac.puk.export_key('PEM').decode('UTF-8'), sig)
        unlocks.append(unlock)

    to = [(lily.wal, 30), (isaac.wal, 2)]
    tx = Tx(unlocks, utxos, to)

    pprint(tx.dict())
    print(tx.create_new_coins())
    siga = tx.unlock[0].sig
    bytelist = []
    for byte in siga:
        bytelist.append(byte)

    attempt = bytes(bytelist)
    pprint(siga)
    pprint(attempt)
    print('testing ', (attempt == siga))
