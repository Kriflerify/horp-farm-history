import json
import pandas as pd
import web3
import pdb
import rewards
from hexbytes import HexBytes

CONTRACT_ADDRESS = '0x2Fc0E2Cfe5D6Ea300D555E5907319a5F7E09884f'
MULTISIG_ADDRESS = '0xF5581dFeFD8Fb0e4aeC526bE659CFaB1f8c781dA'

POOL_ADDRESS = '0x19543B48113EA3243864736F6c634300060c0033'
TOKEN_ADDRESS = '0x92c2fC5F306405eaB0fF0958f6D85d7F8892CF4D'


def read_data():
    global TokenAdded, TokenRemoved, IncentiveClaimed
    with open("data/TokenAdded.json", 'r') as f:
        TokenAdded = json.load(f)
    with open("data/TokenRemoved.json", 'r') as f:
        TokenRemoved = json.load(f)
    with open("data/IncentiveClaimed.json", 'r') as f:
        IncentiveClaimed = json.load(f)

    return TokenAdded, TokenRemoved, IncentiveClaimed

def main():
    logs = read_data()
    headers = ['provider'] + \
        [f"deposit_{i}" for i in range(13)] + \
        [f"reward_{i}" for i in range(13)] + \
        [f"claimed_{i}" for i in range(13)] + \
        [f"removed_{i}" for i in range(14)]
        # [f"total_{i}" for i in range(13)]


    data, eligible_balance = rewards.calc_rewards(*logs)
    
    df = pd.DataFrame(data=data, columns=headers)
    print(df.head())
    


if __name__ == "__main__":
    main()
    
