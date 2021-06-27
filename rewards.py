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
        self.completed_until = -1
        self.deposit = [0]*(TOTAL_CLAIM_PERIOD) # sum of added tokens in corresponding period
        self.removed = [0]*(TOTAL_CLAIM_PERIOD + 1) # sum of removed tokens in correspoing period
                                                    # + 1 because its possible to remove after the claim period
        self.claimed = [0]*(TOTAL_CLAIM_PERIOD) # total reward collected during corresponding period

    def add_token(self, period, amount):
        self.deposit[period] += amount

    def remove_token(self, period, amount):
        self.removed[period] += amount

    def claim_incentive(self, period, amount):
        self.claimed[period] += amount

def transposed_providers():
    index = []
    data = []
    for p in providers.values():
        index += [p.id]
        row = [p.deposit[i] for i in range(TOTAL_CLAIM_PERIOD)]
        row += [p.removed[i] for i in range(TOTAL_CLAIM_PERIOD+1)]
        row += [p.claimed[i] for i in range(TOTAL_CLAIM_PERIOD)]
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


def calc_rewards(TokenAdded, TokenRemoved, IncentiveClaimed):
    ia = ir = ic = 0
    i_period = 0

    while (ia<len(TokenAdded) or ir < len(TokenRemoved) or ic<len(IncentiveClaimed)):
        block_a = TokenAdded[ia]['blockNumber'] if ia<len(TokenAdded) else 999999999
        block_r = TokenRemoved[ir]['blockNumber'] if ir<len(TokenRemoved) else 999999999
        block_c = IncentiveClaimed[ic]['blockNumber'] if ic<len(IncentiveClaimed) else 999999999

        block = min(block_a, block_r, block_c)

        if (distributionBlocks[i_period] < block and i_period <= 13):
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
