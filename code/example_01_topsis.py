"""
示例 01 · 评价类模型：熵权法 + TOPSIS

干什么：给若干个方案（或城市、供应商、医院…）按多个指标排出优劣顺序。
怎么跑：在仓库根目录执行  python code/example_01_topsis.py
产出：控制台排名表 + data/processed/example_01_ranking.csv + figures/example_01_ranking.png

这也是「编程手」在比赛里最常写的一类脚本：数据 → 模型 → 结果 → 图。
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

# 让脚本无论从哪个目录运行，都能 import 到同目录的 plot_setup
sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot_setup import setup  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402

np.random.seed(42)


def build_example_data() -> tuple[pd.DataFrame, list[str]]:
    """造一份示例数据：5 个方案 × 4 个指标。

    指标方向很重要：
      benefit（效益型）= 越大越好，比如治愈率、续航、评分
      cost（成本型）  = 越小越好，比如成本、耗时、污染
    """
    names = ["方案A", "方案B", "方案C", "方案D", "方案E"]
    data = pd.DataFrame({
        "综合成本(万元)": [120, 95, 143, 88, 110],   # 成本型
        "预期收益(分)": [82, 76, 91, 70, 85],        # 效益型
        "实施周期(月)": [10, 8, 14, 7, 9],           # 成本型
        "风险控制(分)": [75, 88, 65, 80, 92],        # 效益型
    }, index=names)
    directions = ["cost", "benefit", "cost", "benefit"]
    return data, directions


def normalize(df: pd.DataFrame, directions: list[str]) -> pd.DataFrame:
    """极差标准化：效益型越大越好，成本型越小越好，统一到 [0,1]。"""
    result = pd.DataFrame(index=df.index, columns=df.columns, dtype=float)
    for col, direction in zip(df.columns, directions):
        x = df[col].astype(float)
        lo, hi = x.min(), x.max()
        if hi == lo:                      # 该指标所有方案相同，视为无区分度
            result[col] = 1.0
        elif direction == "benefit":
            result[col] = (x - lo) / (hi - lo)
        else:                              # 成本型：越小得分越高
            result[col] = (hi - x) / (hi - lo)
    return result


def entropy_weights(norm: pd.DataFrame) -> pd.Series:
    """熵权法求权重：某项指标在各方案间差别越大，它携带的信息越多，权重越高。"""
    p = norm + 1e-12                    # 避免 log(0)
    p = p / p.sum(axis=0)
    n = norm.shape[0]
    e = -(p * np.log(p)).sum(axis=0) / np.log(n)   # 信息熵
    d = 1 - e                                       # 差异系数
    return d / d.sum()


def topsis(norm: pd.DataFrame, weights: pd.Series) -> pd.Series:
    """TOPSIS：算每个方案到「理想最优」和「理想最劣」的距离，越靠近最优越好。"""
    weighted = norm.mul(weights, axis=1)
    best = weighted.max(axis=0)
    worst = weighted.min(axis=0)
    d_best = np.sqrt(((weighted - best) ** 2).sum(axis=1))
    d_worst = np.sqrt(((weighted - worst) ** 2).sum(axis=1))
    return d_worst / (d_best + d_worst)            # 贴近度，越大越好


def main() -> None:
    setup()

    data, directions = build_example_data()
    norm = normalize(data, directions)
    weights = entropy_weights(norm)
    score = topsis(norm, weights).sort_values(ascending=False)

    print("=" * 56)
    print("原始数据")
    print(data.to_string())
    print()
    print("熵权法算出的指标权重")
    for name, w in weights.items():
        print(f"  {name:<14} {w:.4f}")
    print()
    print("TOPSIS 综合得分与排名")
    for rank, (name, s) in enumerate(score.items(), start=1):
        print(f"  第 {rank} 名  {name}   贴近度 = {s:.4f}")
    print("=" * 56)

    # ---------- 存结果 ----------
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    ranking = pd.DataFrame({"方案": score.index, "贴近度": score.values.round(4)})
    ranking.insert(0, "排名", range(1, len(ranking) + 1))
    csv_path = out_dir / "example_01_ranking.csv"
    ranking.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"\n结果已保存：{csv_path}")

    # ---------- 画图 ----------
    fig_dir = Path("figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.2))

    axes[0].barh(score.index[::-1], score.values[::-1], color="#4C8BF5")
    axes[0].set_xlabel("TOPSIS 贴近度")
    axes[0].set_title("各方案综合得分")
    axes[0].set_xlim(0, 1)
    for i, v in enumerate(score.values[::-1]):
        axes[0].text(v + 0.01, i, f"{v:.3f}", va="center", fontsize=9)

    axes[1].barh(weights.index[::-1], weights.values[::-1], color="#F5A623")
    axes[1].set_xlabel("权重")
    axes[1].set_title("熵权法指标权重")
    for i, v in enumerate(weights.values[::-1]):
        axes[1].text(v + 0.005, i, f"{v:.3f}", va="center", fontsize=9)

    fig.tight_layout()
    png_path = fig_dir / "example_01_ranking.png"
    fig.savefig(png_path)
    print(f"图已保存：{png_path}")


if __name__ == "__main__":
    main()
