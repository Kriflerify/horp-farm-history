import json
import pandas as pd
import rewards

CONTRACT_ADDRESS = '0x2Fc0E2Cfe5D6Ea300D555E5907319a5F7E09884f'
MULTISIG_ADDRESS = '0xF5581dFeFD8Fb0e4aeC526bE659CFaB1f8c781dA'

POOL_ADDRESS = '0x19543B48113EA3243864736F6c634300060c0033'
TOKEN_ADDRESS = '0x92c2fC5F306405eaB0fF0958f6D85d7F8892CF4D'

def read_logs():
    global TokenAdded, TokenRemoved, IncentiveClaimed
    with open("data/TokenAdded.json", 'r') as f:
        TokenAdded = json.load(f)
    with open("data/TokenRemoved.json", 'r') as f:
        TokenRemoved = json.load(f)
    with open("data/IncentiveClaimed.json", 'r') as f:
        IncentiveClaimed = json.load(f)

    return TokenAdded, TokenRemoved, IncentiveClaimed

def main():
    logs = read_logs()
    headers = [f"balance_{i}" for i in range(15)] + \
        [f"eligible_balance_{i}" for i in range(13)] + \
        [f"claimed_{i}" for i in range(14)]


    index, data = rewards.bin_by_week(*logs)
    
    df = pd.DataFrame(data=data, index=index, columns=headers)

    total, df = rewards.calc_reward(df)

    df.to_pickle('data/dataFrame.json')
    total.to_pickle('data/total_by_week.json')

    pool_x, pool_y = rewards.get_pool(*logs)
    total_df = pd.DataFrame(data={"block": pool_x, "balance": pool_y})
    total_df.to_pickle('data/total.json')



    # fig, ax = plt.subplots()
    
    # ax.bar(x=list(range(0,14)), height=[df[index[0]][f"reward_{i}"] for i in range(0, 14)])
    # plt.show()
    print(total_df.head())


if __name__ == "__main__":
    main()
    
