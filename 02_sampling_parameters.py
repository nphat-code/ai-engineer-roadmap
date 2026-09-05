"""
02_sampling_parameters.py
-------------------------
BƯỚC 3: SAMPLING PARAMETERS (CÁC THAM SỐ LẤY MẪU)
Bám sát lộ trình roadmap.sh/ai-engineer -> Core LLM Elements:
1. Temperature
2. Top-K
3. Top-P (Nucleus Sampling)
4. Repetition Penalties (Frequency & Presence Penalty)

Mục tiêu:
- Hiểu bản chất toán học của việc LLM "chọn từ tiếp theo" (Next-Token Prediction).
- Tự tay quan sát cách từng tham số thay đổi xác suất đầu ra.
"""

import io
import sys
import math
from typing import Dict, List

if sys.platform == "win32":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console(force_terminal=True)

# Giả sử LLM vừa đọc câu: "Hôm nay trời rất..."
# Mô hình xuất ra điểm số thô (Logits) cho các từ ứng viên trong từ điển:
SAMPLE_LOGITS: Dict[str, float] = {
    "đẹp": 4.5,
    "nắng": 3.8,
    "mát": 3.2,
    "xấu": 2.0,
    "lạ": 1.4,
    "u_ám": 1.0,
    "kỳ_quặc": 0.3,
    "chuối": -1.0,
    "lập_trình": -2.0,
}

def softmax_with_temperature(logits: Dict[str, float], temperature: float) -> Dict[str, float]:
    """
    Công thức Softmax có Temperature:
    P(token_i) = exp(logit_i / T) / sum(exp(logit_j / T))
    - T tiến về 0: Greedy/Argmax -> chọn từ điểm cao nhất với xác suất 100%.
    - T cao: San phẳng phân phối xác suất -> các từ ít gặp có cơ hội được chọn.
    """
    if temperature <= 0.01:
        # Nhiệt độ cực thấp -> 100% chọn từ có logit cao nhất
        best_token = max(logits, key=logits.get) # type: ignore
        return {k: 1.0 if k == best_token else 0.0 for k in logits}

    scaled = {k: v / temperature for k, v in logits.items()}
    max_val = max(scaled.values())  # Kỹ thuật trừ max để tránh tràn số học (numerical stability)
    exp_vals = {k: math.exp(v - max_val) for k, v in scaled.items()}
    sum_exp = sum(exp_vals.values())

    return {k: v / sum_exp for k, v in exp_vals.items()}

def apply_top_k(probabilities: Dict[str, float], top_k: int) -> Dict[str, float]:
    """
    Top-K Sampling:
    Chỉ giữ lại K token có xác suất cao nhất, loại bỏ toàn bộ phần còn lại.
    Sau đó chuẩn hóa lại tổng xác suất các token còn lại về 100%.
    """
    sorted_tokens = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    kept = dict(sorted_tokens[:top_k])
    total = sum(kept.values())
    return {k: (v / total if total > 0 else 0.0) for k, v in kept.items()}

def apply_top_p(probabilities: Dict[str, float], top_p: float) -> Dict[str, float]:
    """
    Top-P (Nucleus Sampling):
    Cộng dồn xác suất từ cao xuống thấp cho đến khi đạt ngưỡng top_p (ví dụ 0.85 = 85%).
    Chỉ giữ lại nhóm token "hạt nhân" đó, cắt bỏ phần đuôi rủi ro.
    """
    sorted_tokens = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    cumulative = 0.0
    kept = {}
    for token, prob in sorted_tokens:
        kept[token] = prob
        cumulative += prob
        if cumulative >= top_p:
            break

    total = sum(kept.values())
    return {k: (v / total if total > 0 else 0.0) for k, v in kept.items()}

def demo_sampling_parameters():
    console.print(Panel(
        "[bold cyan]Prompt đầu vào:[/bold cyan] 'Hôm nay trời rất...'\n"
        "[bold yellow]Mô hình đang dự đoán từ tiếp theo từ các Logits thô.[/bold yellow]",
        title="🔬 BƯỚC 3: CÁC THAM SỐ LẤY MẪU (SAMPLING PARAMETERS)",
        border_style="green"
    ))

    # 1. Hiệu ứng của Temperature
    temps = [0.1, 0.7, 1.5]
    table_t = Table(title="1. Ảnh hưởng của Temperature (T) đến xác suất chọn từ")
    table_t.add_column("Token ứng viên", style="bold")
    table_t.add_column("Logit thô", justify="right", style="dim")
    for t in temps:
        col_style = "green" if t < 0.5 else ("cyan" if t == 0.7 else "magenta")
        table_t.add_column(f"T = {t}", justify="right", style=col_style)

    probs_by_t = {t: softmax_with_temperature(SAMPLE_LOGITS, t) for t in temps}

    for token, logit in SAMPLE_LOGITS.items():
        row = [token, f"{logit:.1f}"]
        for t in temps:
            p = probs_by_t[t].get(token, 0.0) * 100
            row.append(f"{p:.1f}%")
        table_t.add_row(*row)

    console.print(table_t)
    console.print(
        "[dim]• T = 0.1 (Thấp): 99.9% chọn 'đẹp' -> Nhất quán, chính xác (Code, RAG, JSON).\n"
        "• T = 0.7 (Trung bình): Cân bằng giữa logic và tự nhiên (Chatbot).\n"
        "• T = 1.5 (Cao): Các từ hiếm như 'kỳ_quặc', 'chuối' có cơ hội xuất hiện -> Sáng tạo, dễ hallucination.[/dim]\n"
    )

    # 2. Cơ chế lọc Top-K và Top-P (Tại T = 0.7)
    base_probs = softmax_with_temperature(SAMPLE_LOGITS, temperature=0.7)
    top_k_3 = apply_top_k(base_probs, top_k=3)
    top_p_80 = apply_top_p(base_probs, top_p=0.80)

    table_filter = Table(title="2. So sánh bộ lọc Top-K (K=3) vs Top-P (P=0.80) tại T=0.7")
    table_filter.add_column("Token", style="bold")
    table_filter.add_column("Gốc (T=0.7)", justify="right")
    table_filter.add_column("Top-K = 3", justify="right", style="green")
    table_filter.add_column("Top-P = 0.80", justify="right", style="magenta")

    for token in SAMPLE_LOGITS.keys():
        p_orig = base_probs.get(token, 0.0) * 100
        k_str = f"{top_k_3[token]*100:.1f}%" if token in top_k_3 else "[dim red]Bị cắt[/dim red]"
        p_str = f"{top_p_80[token]*100:.1f}%" if token in top_p_80 else "[dim red]Bị cắt[/dim red]"
        table_filter.add_row(token, f"{p_orig:.1f}%", k_str, p_str)

    console.print(table_filter)
    console.print(
        "[dim]• Top-K cắt cố định theo số lượng (chỉ giữ đúng 3 từ đầu).\n"
        "• Top-P cắt linh hoạt theo tổng xác suất tích lũy (giữ đủ 80% độ tin cậy rồi dừng).[/dim]\n"
    )

    # 3. Repetition Penalties
    console.print(Panel(
        "[bold green]3. Repetition Penalties (Chống lặp từ):[/bold green]\n\n"
        "• [cyan]Frequency Penalty (Phạt theo tần suất):[/cyan]\n"
        "  - Trừ điểm logit dựa vào [bold]số lần[/bold] từ đó đã xuất hiện trong bài viết.\n"
        "  - Dùng khi: Muốn AI không nhai đi nhai lại cùng 1 cụm từ hoặc cấu trúc câu.\n\n"
        "• [magenta]Presence Penalty (Phạt theo sự hiện diện):[/magenta]\n"
        "  - Chỉ cần từ/chủ đề đó đã xuất hiện [bold]ít nhất 1 lần[/bold] là bị trừ điểm cố định.\n"
        "  - Dùng khi: Muốn khuyến khích AI mở rộng chủ đề mới, không nói mãi về ý cũ.",
        title="🛡️ Repetition Penalties trong thực tế",
        border_style="yellow"
    ))

if __name__ == "__main__":
    demo_sampling_parameters()
