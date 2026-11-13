"""Replay positions.csv against bars.csv with an explicit cost model.

pnl[i] = position[i] * simple_return[i] - cost_per_side * |position[i] - position[i-1]|
The second term is what the arena means by "no phantom fills": every unit of
position change pays the fee and the slippage, so a strategy that flips every bar
cannot hide its turnover.

  python backtest.py --cost-bp 6
"""
import argparse, csv

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bars", default="bars.csv")
    ap.add_argument("--positions", default="positions.csv")
    ap.add_argument("--cost-bp", type=float, default=6.0)
    a = ap.parse_args()
    closes = [float(r["close"]) for r in csv.DictReader(open(a.bars))]
    pos = [float(r["position"]) for r in csv.DictReader(open(a.positions))]
    cost = a.cost_bp / 10000.0
    rets = [(closes[i + 1] - closes[i]) / closes[i] for i in range(len(closes) - 1)]
    pnl, prev, trades = [], 0.0, 0
    for p, r in zip(pos, rets):
        if abs(p - prev) > 1e-9:
            trades += 1
        pnl.append(p * r - cost * abs(p - prev))
        prev = p
    eq, peak, maxdd = 0.0, 0.0, 0.0
    for x in pnl:
        eq += x
        peak = max(peak, eq)
        maxdd = max(maxdd, peak - eq)
    gross = sum(p * r for p, r in zip(pos, rets))
    print(f"cost      : {a.cost_bp:.0f} bp per side ({cost*100:.2f}%)")
    print(f"trades    : {trades}")
    print(f"gross     : {gross*100:+.2f}%")
    print(f"net       : {eq*100:+.2f}%")
    print(f"max dd    : {maxdd*100:.2f}%")

if __name__ == "__main__":
    main()
