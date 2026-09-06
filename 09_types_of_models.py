"""
09_types_of_models.py
---------------------
BƯỚC THỰC HÀNH: TYPE OF MODELS
Bám sát lộ trình roadmap.sh/ai-engineer -> Type of Models:
1. Pre-trained Models (Base vs Instruct)
2. Closed vs Open Source Models (Trade-offs & Decision Matrix)
3. Self-Hosted Models (VRAM Calculator, Quantization & OpenAI-Compatible API)
"""

import io
import sys
from typing import Dict, Any

if sys.platform == "win32":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console(force_terminal=True)

# =====================================================================
# 1. BẢNG TÍNH VRAM & LƯỢNG TỬ HÓA (QUANTIZATION CALCULATOR)
# =====================================================================
def calculate_vram_requirements(param_billions: float) -> Dict[str, float]:
    """
    Công thức ước lượng VRAM cần thiết để chạy mô hình:
    - FP16 (16-bit float): 2 bytes / tham số + 20% VRAM đệm cho KV Cache
    - INT8 (8-bit quantized): 1 byte / tham số + 20% VRAM đệm
    - INT4 (4-bit quantized - GGUF/AWQ): 0.5 byte / tham số + 20% VRAM đệm
    """
    overhead = 1.20 # 20% bộ nhớ đệm cho ngữ cảnh và activation
    fp16_gb = (param_billions * 2.0) * overhead
    int8_gb = (param_billions * 1.0) * overhead
    int4_gb = (param_billions * 0.5) * overhead
    return {
        "FP16 (Chất lượng gốc)": fp16_gb,
        "INT8 (Nén 8-bit)": int8_gb,
        "INT4 (Nén 4-bit GGUF/AWQ)": int4_gb
    }

def demo_vram_and_quantization():
    console.print(Panel(
        "[bold green]1. BẢNG TÍNH VRAM & LƯỢNG TỬ HÓA (QUANTIZATION) KHI SELF-HOST MÔ HÌNH[/bold green]",
        border_style="cyan"
    ))

    models_to_evaluate = [
        ("Llama-3.2-3B (Nhẹ)", 3.0),
        ("Llama-3.1-8B (Phổ biến nhất)", 8.0),
        ("Qwen-2.5-14B (Cân bằng cao)", 14.0),
        ("Llama-3.3-70B / DeepSeek (Mạnh nhất)", 70.0)
    ]

    table = Table(title="Dung lượng VRAM (Card đồ họa) tối thiểu theo từng mức lượng tử hóa")
    table.add_column("Mô hình", style="bold cyan")
    table.add_column("Số tham số", justify="right")
    table.add_column("FP16 (16-bit)", justify="right", style="dim")
    table.add_column("INT8 (8-bit)", justify="right", style="yellow")
    table.add_column("INT4 (4-bit)", justify="right", style="bold green")
    table.add_column("Phần cứng chạy được (INT4)", style="white")

    for name, params in models_to_evaluate:
        req = calculate_vram_requirements(params)
        hardware = ""
        if req["INT4 (Nén 4-bit GGUF/AWQ)"] <= 8:
            hardware = "Laptop phổ thông / RTX 3060/4060"
        elif req["INT4 (Nén 4-bit GGUF/AWQ)"] <= 16:
            hardware = "RTX 4080 (16GB) / Mac 16GB"
        elif req["INT4 (Nén 4-bit GGUF/AWQ)"] <= 24:
            hardware = "RTX 3090 / 4090 (24GB VRAM)"
        else:
            hardware = "2x - 4x GPU máy chủ A100/H100"

        table.add_row(
            name,
            f"{params}B",
            f"{req['FP16 (Chất lượng gốc)']:.1f} GB",
            f"{req['INT8 (Nén 8-bit)']:.1f} GB",
            f"{req['INT4 (Nén 4-bit GGUF/AWQ)']:.1f} GB",
            hardware
        )
    console.print(table)
    console.print("[dim]💡 Nhờ kỹ thuật INT4 (GGUF), mô hình 8B giảm từ 19.2GB xuống chỉ còn 4.8GB VRAM -> Chạy mượt mà trên laptop cá nhân![/dim]\n")


# =====================================================================
# 2. KIẾN TRÚC OPENAI-COMPATIBLE API (CHUẨN CHUYỂN ĐỔI LINH HOẠT)
# =====================================================================
def demo_openai_compatible_architecture():
    console.print(Panel(
        "[bold green]2. OPENAI-COMPATIBLE CLIENT: CHUYỂN ĐỔI LINH HOẠT GIỮA CLOUD & SELF-HOSTED[/bold green]",
        border_style="yellow"
    ))

    code_snippet = """
    from openai import OpenAI

    # PHƯƠNG ÁN 1: Dùng Cloud Model (Closed Source)
    client_cloud = OpenAI(
        api_key="sk-...",
        base_url="https://api.openai.com/v1"
    )

    # PHƯƠNG ÁN 2: Dùng Self-Hosted Model (vLLM trên Server riêng hoặc Ollama trên máy bàn)
    client_self_hosted = OpenAI(
        api_key="none_needed", # Server nội bộ không bắt buộc key
        base_url="http://localhost:11434/v1" # Endpoint tương thích 100% chuẩn OpenAI!
    )

    # Lệnh gọi API giống hệt nhau 100%, không cần viết lại ứng dụng:
    response = client_self_hosted.chat.completions.create(
        model="llama3.1:8b",
        messages=[{"role": "user", "content": "Xin chào!"}]
    )
    """
    console.print(code_snippet.strip())
    console.print(
        "[bold green]➔ Lợi ích sống còn:[/bold green] Hệ thống của bạn không bao giờ bị phụ thuộc vào một nhà cung cấp (Vendor Lock-in). "
        "Ban ngày có thể dùng GPT-4o, ban đêm hoặc với dữ liệu bảo mật có thể trỏ về cụm vLLM nội bộ trong tích tắc!"
    )


# =====================================================================
# 3. DECISION MATRIX: KHI NÀO CHỌN CLOSED VS OPEN SOURCE?
# =====================================================================
def demo_decision_matrix():
    console.print()
    console.print(Panel(
        "[bold green]3. MA TRẬN QUYẾT ĐỊNH (DECISION MATRIX) CHO DOANH NGHIỆP[/bold green]",
        border_style="magenta"
    ))

    table = Table(title="Khuyến nghị lựa chọn mô hình theo đặc thù bài toán")
    table.add_column("Yêu cầu bài toán", style="bold")
    table.add_column("Lựa chọn khuyến nghị", style="bold green")
    table.add_column("Lý do chuyên môn (Rationale)", style="white")

    table.add_row(
        "Bảo mật dữ liệu tuyệt đối (Ngân hàng, Y tế, Quốc phòng)",
        "Self-Hosted Open Source (Llama 3 / DeepSeek trên on-premise)",
        "Dữ liệu không bao giờ rời khỏi tường lửa nội bộ, tuân thủ nghiêm ngặt chuẩn GDPR/HIPAA."
    )
    table.add_row(
        "Khởi nghiệp / MVP thử nghiệm tính năng nhanh",
        "Closed Source API (GPT-4o mini, Gemini 2.0 Flash)",
        "Chi phí khởi điểm bằng 0, không cần mua sắm hay quản trị hạ tầng GPU phức tạp."
    )
    table.add_row(
        "Tác vụ đặc thù cần độ thông minh đỉnh cao (Suy luận đa bước)",
        "Closed Source (Claude 3.5 Sonnet, GPT-4o)",
        "Khả năng coding và giải quyết logic phức tạp hiện vẫn dẫn đầu thế giới."
    )
    table.add_row(
        "Quy mô cực lớn (> 50 triệu request/tháng cho tác vụ cố định)",
        "Self-Hosted vLLM (Model 8B/14B đã fine-tune)",
        "Chi phí thuê GPU cố định rẻ hơn gấp 10 lần so với trả tiền theo từng triệu token qua API."
    )
    console.print(table)


if __name__ == "__main__":
    demo_vram_and_quantization()
    demo_openai_compatible_architecture()
    demo_decision_matrix()
