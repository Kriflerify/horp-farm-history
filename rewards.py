WEEKLY_INCENTIVE = 384615384615384615384615
WEEKLY_BLOCK_NUMBER = 44800
TOTAL_INCENTIVE = 5000000
TOTAL_CLAIM_PERIOD = 13

startBlock = 12141500

distributionBlocks = [startBlock + i* WEEKLY_BLOCK_NUMBER for i in range(TOTAL_CLAIM_PERIOD+1)]

providers = {}

class Provider:
    def __init__(self, id):
        self.id = id
        self.balance = [0]*(TOTAL_CLAIM_PERIOD + 2) # Balance at end of correspoinding period
        self.eligible_balance = [0]*(TOTAL_CLAIM_PERIOD + 1) # Amount of tokens locked from end of period i to next one
        self.claimed = [0]*(TOTAL_CLAIM_PERIOD + 1) # total reward collected during corresponding period

    def next_period(self, ending_period):
        self.balance[ending_period+1] = self.balance[ending_period]
        if (ending_period < TOTAL_CLAIM_PERIOD-1):
            self.eligible_balance[ending_period+1] = self.balance[ending_period]

    def add_token(self, period, amount):
        self.balance[period] += amount
        self.eligible_balance[period] += amount

    def remove_token(self, period, amount):
        self.balance[period] -= amount
        if (period < TOTAL_CLAIM_PERIOD):
            self.eligible_balance[period] -= amount
        if (period > 0):
            self.eligible_balance[period-1] = min(self.eligible_balance[period-1], \
                self.balance[period])

    def claim_incentive(self, period, amount):
        self.claimed[period] += amount

def transposed_providers():
    index = []
    data = []
    for p in providers.values():
        index += [p.id]
        row = [p.balance[i] for i in range(TOTAL_CLAIM_PERIOD + 2)]
        row += [p.eligible_balance[i] for i in range(TOTAL_CLAIM_PERIOD)]
        row += [p.claimed[i] for i in range(TOTAL_CLAIM_PERIOD + 1)]
        data += [row]
    return index, data
    

def process_token_added(log):
    id = int(log['topics'][1], 16)
    if (id not in providers):
        providers[id] = Provider(id)
    period = int(log['topics'][2], 16)
    amount = int(log['data'], 16)

    providers[id].add_token(period, amount)


def process_token_removed(log):
    id = int(log['topics'][1], 16)
    period = int(log['topics'][2], 16)
    amount = int(log['data'], 16)
    assert id in providers

    providers[id].remove_token(period, amount)


def process_incentive_claimed(log):
    id = int(log['topics'][1], 16)
    until = int(log['topics'][2], 16)
    amount = int(log['data'], 16)
    assert id in providers

    providers[id].claim_incentive(until, amount)


def bin_by_week(TokenAdded, TokenRemoved, IncentiveClaimed):
    ia = ir = ic = 0
    i_period = 0

    while (ia<len(TokenAdded) or ir < len(TokenRemoved) or ic<len(IncentiveClaimed)):
        block_a = TokenAdded[ia]['blockNumber'] if ia<len(TokenAdded) else 999999999
        block_r = TokenRemoved[ir]['blockNumber'] if ir<len(TokenRemoved) else 999999999
        block_c = IncentiveClaimed[ic]['blockNumber'] if ic<len(IncentiveClaimed) else 999999999

        block = min(block_a, block_r, block_c)

        if (i_period <= TOTAL_CLAIM_PERIOD and distributionBlocks[i_period] < block):
            for p in providers.values():
                p.next_period(i_period)
            i_period += 1
        else:
            if (block == block_a):
                process_token_added(TokenAdded[ia])
                ia += 1
            elif (block == block_r):
                process_token_removed(TokenRemoved[ir])
                ir += 1
            elif (block == block_c):
                process_incentive_claimed(IncentiveClaimed[ic])
                ic += 1

    return transposed_providers()

def calc_reward(df):
    t = df.sum()
    print(t)
    df['reward_0'] = 0
    for i in range(1, TOTAL_CLAIM_PERIOD + 1):
        df[f"reward_{i}"] = (WEEKLY_INCENTIVE * df[f"eligible_balance_{i-1}"]) / t[f"eligible_balance_{i-1}"]
        df[f"reward_{i}"] += df[f"reward_{i-1}"] - df[f"claimed_{i-1}"]

    t = df.sum()
    return t, df

def get_pool(TokenAdded, TokenRemoved, IncentiveClaimed):
    pool_x = [0]
    pool_y = [0]

    ia = ir = ic = 0
    i_period = 0

    while (ia<len(TokenAdded) or ir < len(TokenRemoved)):
        block_a = TokenAdded[ia]['blockNumber'] if ia<len(TokenAdded) else 999999999
        block_r = TokenRemoved[ir]['blockNumber'] if ir<len(TokenRemoved) else 999999999

        block = min(block_a, block_r)

        pool_x += [block]
        if block == block_a:
            log = TokenAdded[ia]
            amount = int(log['data'], 16)
            pool_y += [pool_y[-1] + amount]
            ia += 1
        elif block == block_r:
            log == TokenRemoved[ir]
            amount = int(log['data'], 16)
            pool_y += [pool_y[-1] - amount]
            ir += 1

    pool_x = pool_x[1:]
    pool_y = pool_y[1:]
    return pool_x, pool_y
