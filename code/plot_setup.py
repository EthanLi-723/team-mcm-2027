"""
画图统一样式：中文正常显示 + 论文级别的图表参数。

用法（每个画图脚本开头加一行）：
    from plot_setup import setup
    setup()
"""

import matplotlib
import matplotlib.pyplot as plt


def setup(font_size: int = 12, dpi: int = 300) -> None:
    """设置中文显示与统一的图样式。"""
    # Windows 常见中文字体，按可用性从前到后挑
    matplotlib.rcParams["font.sans-serif"] = [
        "Microsoft YaHei",
        "SimHei",
        "SimSun",
        "KaiTi",
    ]
    # 负号显示为正常减号，否则坐标轴负号会变方块
    matplotlib.rcParams["axes.unicode_minus"] = False

    matplotlib.rcParams.update({
        "figure.dpi": 120,          # 屏幕预览
        "savefig.dpi": dpi,         # 论文出图分辨率
        "savefig.bbox": "tight",    # 去掉多余白边
        "font.size": font_size,
        "axes.titlesize": font_size + 2,
        "axes.labelsize": font_size,
        "legend.fontsize": font_size - 1,
        "xtick.labelsize": font_size - 1,
        "ytick.labelsize": font_size - 1,
        "axes.grid": True,
        "grid.alpha": 0.3,
        "grid.linestyle": "--",
        "axes.facecolor": "white",
        "figure.facecolor": "white",
    })


if __name__ == "__main__":
    setup()
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.plot([1, 2, 3, 4], [1, 1.6, 2.1, 2.4], marker="o", label="示例曲线")
    ax.set_title("中文标题测试：模型拟合效果")
    ax.set_xlabel("时间（天）")
    ax.set_ylabel("指标值")
    ax.legend()
    fig.savefig("figures/plot_setup_测试.png")
    print("已生成 figures/plot_setup_测试.png，标题和坐标轴中文应正常显示。")
