WEEKLY_INCENTIVE = 384615384615384615384615
WEEKLY_BLOCK_NUMBER = 44800
TOTAL_INCENTIVE = 5000000
TOTAL_CLAIM_PERIOD = 13

startBlock = 12141500

distributionBlocks = [startBlock + i* WEEKLY_BLOCK_NUMBER for i in range(TOTAL_CLAIM_PERIOD+1)]

pool = [0] * (TOTAL_CLAIM_PERIOD + 1) # balance of deposited tokens eligible to produce reward at corresponding period

providers = {}

class Provider:
    def __init__(self, id):
        self.id = id
        self.completed_until = -1
        self.deposit = [0]*(TOTAL_CLAIM_PERIOD) # sum of added tokens in corresponding period
        self.removed = [0]*(TOTAL_CLAIM_PERIOD + 1) # sum of removed tokens in correspoing period
                                                    # + 1 because its possible to remove after the claim period
        self.reward = [0]*(TOTAL_CLAIM_PERIOD) # total reward earned during corresponding period
        self.claimed = [0]*(TOTAL_CLAIM_PERIOD) # total reward collected during corresponding period
        self.accumulated_reward = 0 # The total reward that could be claimed
        self.balance = 0 # Deposited tokens
        self.balance_at_last_claim = 0 # Needed to calculate reward since last claim

    def add_rewards_until(self, period):
        assert period > self.completed_until, "Trying to calculate incentives for a week that has already been processed"
        for i in range(self.completed_until + 1, period + 1):
            self.balance_at_last_claim += self.deposit[i] - self.removed[i]
            reward = (WEEKLY_INCENTIVE *self.balance_at_last_claim) // pool[i]
            print(f"{self.balance_at_last_claim}, -- , {pool[i]}")
            # print(f"balance: {self.balance_at_last_claim}, acc reward: {self.accumulated_reward}, new reward: {reward}, pool: {pool[i]}")
            self.reward[i] += reward
            self.accumulated_reward += reward
        self.completed_until = period

    def add_token(self, period, amount):
        assert period > self.completed_until, "Trying to deposit token for a week whose rewards have already been calculated"
        self.deposit[period] += amount
        self.balance += amount
        
    def claim_incentive(self, period, amount):
        assert period <= self.completed_until, "Trying to claim token for a week whose rewards have already been calculated"
        self.claimed[period] += amount
        if (not amount == self.accumulated_reward):
            print(f"Claimed {amount} of reward but should claim {self.accumulated_reward}")
            if (self.accumulated_reward == self.reward[period]):
                print(f"SOL: {amount}, PYTHON: {self.accumulated_reward}")
                print(f"BALANCEATLASTCLAIM: {self.balance_at_last_claim}, pool: {pool[period]}")
        self.accumulated_reward = 0

    def remove_token(self, period, amount):
        assert period > self.completed_until, "Trying to remove deposit from a week whose rewards have already been calculated"
        if (self.balance < amount):
            print(f"Trying to remove {amount}, but only have {self.deposit[period]} tokens deposited, for account {self.id}, period {period}")

        self.removed[period] += amount
        self.balance -= amount

def transposed_providers():
    columns = []
    for p in providers.values():
        row = [p.id]
        row += [p.deposit[i] for i in range(TOTAL_CLAIM_PERIOD)]
        row += [p.reward[i] for i in range(TOTAL_CLAIM_PERIOD)]
        row += [p.claimed[i] for i in range(TOTAL_CLAIM_PERIOD)]
        row += [p.removed[i] for i in range(TOTAL_CLAIM_PERIOD+1)]
        columns += [row]
    return columns, pool
    

def process_token_added(log, i_period):
    id = int(log['topics'][1], 16)
    if (id not in providers):
        providers[id] = Provider(id)
    period = int(log['topics'][2], 16)
    amount = int(log['data'], 16)

    pool[period] += amount
    providers[id].add_token(period, amount)


def process_token_removed(log, i_period):
    id = int(log['topics'][1], 16)
    period = int(log['topics'][2], 16)
    amount = int(log['data'], 16)
    assert id in providers

    pool[period] -= amount
    providers[id].remove_token(period, amount)


def process_incentive_claimed(i_period, log):
    id = int(log['topics'][1], 16)
    until = int(log['topics'][2], 16)
    amount = int(log['data'], 16)
    assert id in providers
    assert i_period - 1 == until

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
            for p in providers.values():
                p.add_rewards_until(i_period)
            pool[i_period + 1] = pool[i_period]
            i_period += 1
        else:
            if (block == block_a):
                process_token_added(TokenAdded[ia], i_period)
                ia += 1

            elif (block == block_r):
                process_token_removed(TokenRemoved[ir], i_period)
                ir += 1

            elif (block == block_c):
                process_incentive_claimed(i_period, IncentiveClaimed[ic])
                ic += 1

    return transposed_providers()
