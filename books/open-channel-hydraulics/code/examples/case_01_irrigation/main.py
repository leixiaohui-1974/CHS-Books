# --- CHS AUTOMATED ENVIRONMENT FIX ---
import sys, os
# Super safe I/O override for Windows legacy scripts
class SafeWriter:
    def __init__(self, target):
        self.target = target
    def write(self, s):
        try:
            self.target.write(s)
        except UnicodeEncodeError:
            self.target.write(s.encode('utf-8', 'backslashreplace').decode('gbk', 'ignore'))
    def flush(self):
        if hasattr(self.target, 'flush'): self.target.flush()
    def __getattr__(self, name):
        return getattr(self.target, name)

if not getattr(sys.stdout, '_chs_safe', False):
    sys.stdout = SafeWriter(sys.stdout)
    sys.stdout._chs_safe = True
if not getattr(sys.stderr, '_chs_safe', False):
    sys.stderr = SafeWriter(sys.stderr)
    sys.stderr._chs_safe = True

_current_dir = os.path.dirname(os.path.abspath(__file__))
for i in range(4):
    _test_path = os.path.abspath(os.path.join(_current_dir, *(['..'] * i)))
    if os.path.exists(os.path.join(_test_path, 'core')) or os.path.exists(os.path.join(_test_path, 'gwflow')) or os.path.exists(os.path.join(_test_path, 'models')) or os.path.exists(os.path.join(_test_path, 'code', 'core')):
        if _test_path not in sys.path:
            sys.path.insert(0, _test_path)
        code_dir = os.path.join(_test_path, 'code')
        if os.path.exists(code_dir) and code_dir not in sys.path:
            sys.path.insert(0, code_dir)
        break
# -------------------------------------
from __future__ import annotations
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

@dataclass(frozen=True)
class CaseInput:
    Q: float = 0.5
    b: float = 1.0
    m: float = 1.5
    S0: float = 2e-4
    n: float = 0.025
    g: float = 9.81

def hydraulic_elements(h: float, p: CaseInput) -> dict:
    if h <= 0: raise ValueError("Depth h must be positive.")
    A = (p.b + p.m * h) * h
    P = p.b + 2.0 * h * math.sqrt(1.0 + p.m ** 2)
    R = A / P
    B = p.b + 2.0 * p.m * h
    D = A / B
    v = (1.0 / p.n) * (R ** (2.0 / 3.0)) * math.sqrt(p.S0)
    Q = A * v
    Fr = v / math.sqrt(p.g * D)
    return {"h": h, "A": A, "P": P, "R": R, "B": B, "D": D, "v": v, "Q": Q, "Fr": Fr}

def discharge_for_depth(h: float, p: CaseInput) -> float:
    return hydraulic_elements(h, p)["Q"]

def solve_normal_depth(p: CaseInput, tol: float = 1e-10, max_iter: int = 100) -> tuple[float, int, float]:
    low, high = 1e-4, 1.0
    while discharge_for_depth(high, p) < p.Q:
        high *= 1.5
        if high > 100: raise RuntimeError("Failed to bracket normal depth.")

    h = 0.5 * (low + high)
    for i in range(1, max_iter + 1):
        Qh = discharge_for_depth(h, p)
        res = Qh - p.Q
        if abs(res) <= tol: return h, i, res
        dh = max(1e-6, h * 1e-6)
        dQdh = (discharge_for_depth(h + dh, p) - Qh) / dh

        if res > 0: high = h
        else: low = h

        if abs(dQdh) < 1e-12: h_new = 0.5 * (low + high)
        else:
            h_new = h - res / dQdh
            if not (low < h_new < high): h_new = 0.5 * (low + high)
        h = h_new

    raise RuntimeError("Normal depth solver did not converge.")

def plot_qh_curve(p: CaseInput, h_star: float, out_png: Path) -> None:
    h_arr = np.linspace(0.2, 1.6, 200)
    q_arr = np.array([discharge_for_depth(float(h), p) for h in h_arr])
    plt.figure(figsize=(8, 5))
    plt.plot(q_arr, h_arr, lw=2, label="Q-h curve")
    plt.scatter([p.Q], [h_star], c="red", zorder=3, label=f"design point ({p.Q:.2f}, {h_star:.3f})")
    plt.xlabel("Q (m^3/s)")
    plt.ylabel("h (m)")
    plt.title("Uniform Flow Manning Q-h Relation (Case 1)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, dpi=150)
    plt.close()

def run_case() -> dict:
    p = CaseInput()
    h, iters, residual = solve_normal_depth(p)
    elems = hydraulic_elements(h, p)
    return {
        "input": asdict(p),
        "solver": {"iterations": iters, "residual_Q": residual},
        "result": elems
    }

if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    result = run_case()
    
    json_path = out_dir / "results_refined.json"
    json_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    
    plot_path = out_dir / "q_h_curve.png"
    p = CaseInput(**result["input"])
    plot_qh_curve(p, result["result"]["h"], plot_path)
    print("Execution complete. Found normal depth: ", result["result"]["h"])