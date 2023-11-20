import sys
from web3 import Web3
from eth_account.account import Account
from hdwallet import BIP44HDWallet
from hdwallet.cryptocurrencies import EthereumMainnet
from hdwallet.derivations import BIP44Derivation
from hdwallet.utils import generate_mnemonic
from typing import Optional
from colorama import Fore, Style
import multiprocessing

cores = 8
r=1

def connect():
    print("[INFO] Connecting to Ethereum mainnet ...")
    try:
        web3Instance = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))
    except:
        sys.exit("[ERROR] There was an error with connecting to the Infura APIs. Check your API key and the config file for issues.")
    # Double check our connection works
    if not web3Instance.is_connected():
        sys.exit("[ERROR] Cannot connect to given URL. Please verify the correctness of the URL and if the site is online.")
    
    print("[INFO] Connected to Ethereum mainnet ...")
    return web3Instance

def generateAddress(entropy):
    try:
        tempAcct = Account.create(extra_entropy=entropy)
    except: 
        sys.exit("[ERROR] There was an an issue creating a wallet with this entropy input.")
    pubKey = tempAcct.address # Public key/address
    privKey = tempAcct.key # Private key
    return pubKey, privKey

def main(r):
    z = 1
    w = 0
    web3Instance = connect()
    while True:
        MNEMONIC: str = generate_mnemonic(language="english", strength=128)
        PASSPHRASE: Optional[str] = None
        bip44_hdwallet: BIP44HDWallet = BIP44HDWallet(cryptocurrency=EthereumMainnet)
        bip44_hdwallet.from_mnemonic(
            mnemonic=MNEMONIC, language="english", passphrase=PASSPHRASE
        )
        bip44_hdwallet.clean_derivation()
        for address_index in range(3):
            # Derivation from Ethereum BIP44 derivation path
            bip44_derivation: BIP44Derivation = BIP44Derivation(
                cryptocurrency=EthereumMainnet, account=0, change=False, address=address_index
            )
            # Drive Ethereum BIP44HDWallet
            bip44_hdwallet.from_path(path=bip44_derivation)
            # Print address_index, path, address and private_key
            addr = bip44_hdwallet.address()
            priv = bip44_hdwallet.private_key()
            # print(Fore.WHITE, f"({address_index}) {bip44_hdwallet.path()} {bip44_hdwallet.address()} 0x{bip44_hdwallet.private_key()} : multi {r}")
            print(Fore.YELLOW,'Total Scan:',Fore.WHITE, str(z),Fore.YELLOW,'Winner Wallet:',Fore.GREEN, str(w), Fore.YELLOW, 'Checking Now ----- ETH Address', Fore.WHITE, str(addr), end='\r')
                
            sys.stdout.flush()
            z += 8
            transtion_count = web3Instance.eth.get_transaction_count(addr)
            if transtion_count > 0:
                print('Winning', Fore.GREEN, str(w), Fore.WHITE, str(z), Fore.YELLOW, 'Total Scan Checking ----- ETH Address =', Fore.GREEN, str(addr), end='\r')
                w += 1
                f = open("Results.txt", "a")
                f.write('\nAddress = ' + str(addr))
                f.write('\nPrivate Key = ' + str(priv))
                f.write('\n=========================================================\n')
                f.close()
                print('Winner information Saved On text file = ADDRESS ', str(addr))
                continue
            bip44_hdwallet.clean_derivation()
            # time.sleep(0.2)

if __name__=="__main__":
    jobs = []
    for r in range(cores):
        p = multiprocessing.Process(target=main, args=(r,))
        jobs.append(p)
        p.start()