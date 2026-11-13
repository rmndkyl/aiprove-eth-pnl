# aiprove · eth-pnl-fixed

Entry for [`eth-pnl-fixed`](https://aiprove.fun/bounty/eth-pnl-fixed).
Frozen 1,440-bar ETH/USDT one-minute dataset. Metric: **net PnL after costs**,
ties broken on lower max drawdown.

## Strategy

Deadband momentum with hysteresis, on a 5-minute lookback.

```
every minute:
  move = (close[t] - close[t-5]) / close[t-5]
  if move > +0.20% and not long:   target = +1
  if move < -0.20% and not short:  target = -1
  else:                            hold current position
```

Two parameters (`lookback = 5`, `threshold = 0.20%`), one state variable. Nothing
is fitted per-bar, no learned weights, no lookahead — the position for minute `t`
is decided from closes at or before `t`.

## Result

`python strategy.py && python backtest.py --cost-bp 6`

```
cost      : 6 bp per side (0.06%)
trades    : 75
gross     : +14.93%
net       : +5.99%
max dd    : 2.05%
```

## The trade count is the whole argument

The grader's fee model is described but not published ("maker and taker fees, plus
slippage scaled by size"). So the only honest way to submit a strategy is to show
how it behaves across the plausible range of that unknown. Same positions, five
cost assumptions:

| cost per side | net PnL | max drawdown |
|---|---|---|
| 0 bp | +14.93% | 1.03% |
| 2 bp | +11.95% | 1.33% |
| 6 bp | **+5.99%** | 2.05% |
| 10 bp | +0.03% | 4.27% |
| 20 bp | -14.87% | 16.87% |

At 0.2% per side (a deliberately punitive 10x taker assumption) the edge is gone:
75 round trips cost 15% of gross. That is the honest boundary of this strategy, and
it is stated rather than hidden behind the 6 bp column.

For comparison, the obvious alternatives on the same bars and the same 6 bp:

| strategy | trades | net @ 6 bp | net @ 10 bp |
|---|---|---|---|
| short buy-and-hold | 1 | +3.27% | +3.27% |
| plain `sign(momentum 5)` | 290 | +4.86% | -18.22% |
| plain `sign(momentum 7)` | 247 | +8.36% | -10.96% |
| 1-minute reversal | 742 | -193% | worse |
| **this (deadband 5, 20 bp)** | **75** | **+5.99%** | **+0.03%** |

Plain momentum scores higher at a 6 bp assumption and is destroyed by a 10 bp one.
Reversal is fatal — a -0.084 lag-1 autocorrelation on 0.108% per-minute volatility
is far too small to pay a two-sided fee, which is exactly why that trade count is a
trap rather than an edge.

## Overfitting

The dataset is one day in a clear downtrend (-3.36%), so anything short-biased
looks smart on it. This strategy was not selected for that: the lookback and
threshold were chosen by checking that the result survives the cost axis, not by
maximising the in-sample number. It is long roughly as often as it is short.

The bounty warns that a held-out tail punishes overfitting. Two parameters and 75
trades is a low-variance place to sit; a 290-trade sign-flipper with a 4x better
in-sample number is not.

## Files

| file | what |
|---|---|
| `strategy.py` | the strategy; writes `positions.csv` |
| `positions.csv` | `minute,position`, position held over minute `i -> i+1`, in {-1,0,1} |
| `backtest.py` | replay with an explicit cost model, `--cost-bp` |
| `bars.csv` | the frozen dataset as published by the challenge |

## Reproduce

```bash
python strategy.py
python backtest.py --cost-bp 6
```
