"""
示例 02 · 预测类模型：灰色预测 GM(1,1) + 线性回归对比

干什么：用很少的历史数据（4~10 个点）预测未来几期的走势。
为什么用它：国赛/美赛常给"小样本"序列（几年数据），GM(1,1) 不需要大样本就能用。
怎么跑：在仓库根目录执行  python code/example_02_gm11_forecast.py
产出：控制台结果 + data/processed/example_02_forecast.csv + figures/example_02_forecast.png
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plot_setup import setup  # noqa: E402

import matplotlib.pyplot as plt  # noqa: E402


def gm11(x0: np.ndarray, periods: int = 3) -> tuple[np.ndarray, np.ndarray, float, float]:
    """灰色预测 GM(1,1)。

    返回：(拟合值, 预测值, 发展系数 a, 灰作用量 b)
    """
    n = len(x0)
    x1 = np.cumsum(x0)                      # 1-AGO 累加生成
    z1 = 0.5 * (x1[1:] + x1[:-1])           # 紧邻均值生成

    B = np.column_stack([-z1, np.ones(n - 1)])
    Y = x0[1:]                              # 保持一维，和 B 的行数对应
    # 最小二乘解 (B^T B)^-1 B^T Y
    params = np.linalg.lstsq(B, Y, rcond=None)[0]
    a, b = float(params[0]), float(params[1])

    def x1_hat(k: int) -> float:            # 时间响应函数，k 从 1 开始
        return (x0[0] - b / a) * np.exp(-a * (k - 1)) + b / a

    fitted = np.array([x1_hat(k) for k in range(1, n + periods + 1)])
    restored = np.diff(np.concatenate([[0], fitted]))       # 累减还原

    return restored[:n], restored[n:n + periods], a, b


def posterior_check(x0: np.ndarray, x0_hat: np.ndarray) -> tuple[float, float]:
    """后验差检验：C 越小越好，P 越大越好。

    精度等级参考：C < 0.35 且 P > 0.95 → 一级（好）
    """
    residual = x0 - x0_hat
    s1 = np.std(x0, ddof=1)
    s2 = np.std(residual, ddof=1)
    C = float(s2 / s1) if s1 > 0 else float('inf')
    P = float(np.mean(np.abs(residual - residual.mean()) < 0.6745 * s1))
    return C, P


def main() -> None:
    setup()

    # 示例：某医院 2019—2025 年的专科门诊量（万次），只有 7 个点
    years = np.arange(2019, 2026)
    values = np.array([12.4, 13.9, 15.1, 17.6, 19.2, 22.4, 24.8], dtype=float)

    fitted, forecast, a, b = gm11(values, periods=3)
    C, P = posterior_check(values, fitted)

    # 线性回归作为对比
    coef = np.polyfit(years, values, 1)
    linear_fit = np.polyval(coef, years)
    future_years = np.arange(years[-1] + 1, years[-1] + 1 + len(forecast))
    linear_forecast = np.polyval(coef, future_years)

    # 误差指标
    mape_gm = float(np.mean(np.abs((values - fitted) / values)) * 100)
    mape_lr = float(np.mean(np.abs((values - linear_fit) / values)) * 100)

    print("=" * 60)
    print("原始数据")
    for y, v in zip(years, values):
        print(f"  {y}  {v:6.2f}")
    print()
    print(f"GM(1,1) 参数：发展系数 a = {a:.4f}，灰作用量 b = {b:.4f}")
    print(f"后验差检验：C = {C:.4f}（<0.35 为一级），P = {P:.2f}（>0.95 为一级）")
    print(f"拟合精度：GM(1,1) MAPE = {mape_gm:.2f}%   线性回归 MAPE = {mape_lr:.2f}%")
    print()
    print("未来三年预测")
    for y, v_gm, v_lr in zip(future_years, forecast, linear_forecast):
        print(f"  {y}  GM(1,1): {v_gm:6.2f}    线性回归: {v_lr:6.2f}")
    print("=" * 60)

    # ---------- 存结果 ----------
    out_dir = Path("data/processed")
    out_dir.mkdir(parents=True, exist_ok=True)
    table = pd.DataFrame({
        "年份": list(years) + list(future_years),
        "实际值": list(values) + [None] * len(future_years),
        "GM(1,1)": list(fitted.round(3)) + list(forecast.round(3)),
        "线性回归": list(linear_fit.round(3)) + list(linear_forecast.round(3)),
    })
    csv_path = out_dir / "example_02_forecast.csv"
    table.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"\n结果已保存：{csv_path}")

    # ---------- 画图 ----------
    fig_dir = Path("figures")
    fig_dir.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.plot(years, values, "o-", label="实际值", color="#1f77b4", linewidth=2)
    ax.plot(years, fitted, "s--", label=f"GM(1,1) 拟合（MAPE {mape_gm:.2f}%）",
            color="#F5A623", linewidth=1.6)
    ax.plot(years, linear_fit, "^:", label=f"线性回归（MAPE {mape_lr:.2f}%）",
            color="#7f7f7f", linewidth=1.6)
    ax.plot(future_years, forecast, "s--", color="#F5A623", linewidth=2, alpha=0.7)
    ax.plot(future_years, linear_forecast, "^:", color="#7f7f7f", linewidth=2, alpha=0.7)
    ax.axvspan(years[-1], future_years[-1], color="#FFE9C7", alpha=0.5)
    ax.text(years[-1] + 0.1, values.min(), "预测区间", fontsize=9, color="#8a6d3b")
    ax.set_xlabel("年份")
    ax.set_ylabel("门诊量（万次）")
    ax.set_title("门诊量预测：灰色预测 GM(1,1) 与线性回归对比")
    ax.legend()
    ax.set_xticks(list(years) + list(future_years))
    fig.tight_layout()
    png_path = fig_dir / "example_02_forecast.png"
    fig.savefig(png_path)
    print(f"图已保存：{png_path}")


if __name__ == "__main__":
    main()
