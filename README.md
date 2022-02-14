# Hopr Liquidity Mining program "dashboard" 
Attempting [this](https://gitcoin.co/issue/hoprnet/hopr-analytics/6) bounty.

## Execution
1. Open fetch.ipynb, if necessary adjust the web3 endpoint or contract address or startblocks
2. Do Steps `#1)`, `#2)`, `#3b)`, `#4b)` to fetch all events where Tokens were Removed, added or Incentives claimed and write them to json files in `data/TokenAdded.json`, `data/TokenRemoved.json`, `data/IncentiveClaimed.json`.
3. Run `python3 createDataFrames.py`
4. Open Dashboard.ipynb and run everything
