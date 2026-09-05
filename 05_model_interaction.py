"""
05_model_interaction.py
-----------------------
BƯỚC THỰC HÀNH: MODEL INTERACTION
Bám sát lộ trình roadmap.sh/ai-engineer -> Prompt Engineering:
1. Function Calling (Tool Use)
2. Prompt Caching (Cơ chế & Toán kinh tế)
3. Streaming Responses (TTFT - Time To First Token)
"""

import io
import sys
import time
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
# 1. MÔ PHỎNG FUNCTION CALLING (TOOL USE)
# =====================================================================
# Giả sử ta có 1 hàm nghiệp vụ tra cứu đơn hàng thực tế
def get_order_status(order_id: str) -> Dict[str, Any]:
    """Hàm Python thực tế chạy ở Backend kết nối cơ sở dữ liệu"""
    database = {
        "DH-888": {"status": "Đang vận chuyển", "shipper": "Nguyễn Văn A (0912345678)", "eta": "15:30 chiều nay"},
        "DH-999": {"status": "Đã giao thành công", "recipient": "Trần Thị B", "date": "04/09/2026"}
    }
    return database.get(order_id, {"error": "Không tìm thấy mã đơn hàng trong hệ thống"})

# Khai báo Tool Schema cho LLM (JSON Schema)
ORDER_TOOL_SCHEMA = {
    "name": "get_order_status",
    "description": "Tra cứu trạng thái, người giao hàng và thời gian dự kiến của một mã đơn hàng cụ thể.",
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "Mã đơn hàng, ví dụ: DH-888, DH-999"
            }
        },
        "required": ["order_id"]
    }
}

def demo_function_calling():
    console.print(Panel("[bold green]1. FUNCTION CALLING (Cơ chế gọi công cụ bên ngoài của AI Agent)[/bold green]", border_style="cyan"))

    user_query = "Kiểm tra giúp tôi đơn hàng DH-888 xem khi nào giao tới?"
    console.print(f"[bold cyan]User:[/bold cyan] {user_query}\n")

    # BƯỚC 1: LLM nhận prompt + Tool schema, nhận diện cần gọi hàm
    console.print("[dim]➔ Bước 1: LLM phân tích thấy cần dùng công cụ 'get_order_status'...[/dim]")
    llm_tool_call_request = {
        "tool_call": {
            "name": "get_order_status",
            "arguments": {"order_id": "DH-888"}
        }
    }
    console.print(Panel(
        f"[bold yellow]LLM quyết định gọi hàm:[/bold yellow] {llm_tool_call_request['tool_call']['name']}\n"
        f"[bold yellow]Tham số bóc tách được:[/bold yellow] {llm_tool_call_request['tool_call']['arguments']}",
        title="🤖 LLM Tool Call Request",
        border_style="yellow"
    ))

    # BƯỚC 2: Backend thực thi hàm Python thực tế
    console.print("[dim]➔ Bước 2: Backend thực thi hàm Python và truy vấn Database...[/dim]")
    target_id = llm_tool_call_request["tool_call"]["arguments"]["order_id"]
    execution_result = get_order_status(target_id)
    console.print(Panel(
        f"{execution_result}",
        title="⚙️ Kết quả Backend trả về (Tool Output)",
        border_style="magenta"
    ))

    # BƯỚC 3: Gửi kết quả ngược lại cho LLM để tổng hợp câu trả lời tự nhiên
    console.print("[dim]➔ Bước 3: Gửi kết quả trên lại cho LLM để tạo câu trả lời hoàn chỉnh...[/dim]")
    final_response = (
        f"Đơn hàng **{target_id}** của bạn hiện **{execution_result['status']}**! "
        f"Shipper phụ trách là **{execution_result['shipper']}** và dự kiến sẽ giao tới vào khoảng **{execution_result['eta']}**."
    )
    console.print(Panel(final_response, title="✅ Câu trả lời cuối cùng cho User", border_style="green"))


# =====================================================================
# 2. TOÁN KINH TẾ & CƠ CHẾ PROMPT CACHING
# =====================================================================
def demo_prompt_caching():
    console.print()
    console.print(Panel("[bold green]2. PROMPT CACHING (Tối ưu 80-90% chi phí cho ngữ cảnh lớn)[/bold green]", border_style="yellow"))

    # Giả sử bạn xây dựng chatbot hỏi đáp tài liệu công ty (PDF 200 trang = 100,000 tokens)
    cached_tokens = 100_000
    new_user_tokens = 200
    daily_requests = 5_000

    # Bảng giá chuẩn của Claude 3.5 Sonnet / Gemini 1.5 Pro (USD / 1M tokens)
    COST_UNCACHED_INPUT = 3.00   # $3 / 1M tokens
    COST_CACHED_INPUT = 0.30     # $0.30 / 1M tokens (Giảm tới 90%)

    # Chi phí mỗi ngày KHÔNG dùng cache
    daily_uncached = (daily_requests * (cached_tokens + new_user_tokens) / 1_000_000) * COST_UNCACHED_INPUT
    
    # Chi phí mỗi ngày CÓ dùng cache (chỉ trả phí full cho lần nạp đầu tiên, còn lại hưởng giá cache)
    daily_cached = (daily_requests * cached_tokens / 1_000_000) * COST_CACHED_INPUT + (daily_requests * new_user_tokens / 1_000_000) * COST_UNCACHED_INPUT

    table = Table(title="So sánh chi phí khi có và không có Prompt Caching (Ngữ cảnh 100k tokens, 5.000 requests/ngày)")
    table.add_column("Phương án", style="bold")
    table.add_column("Chi phí / Ngày", justify="right")
    table.add_column("Chi phí / Tháng (30 ngày)", justify="right", style="bold green")
    table.add_column("Tỷ lệ tiết kiệm", justify="right", style="bold magenta")

    table.add_row("Không dùng Cache", f"${daily_uncached:.2f}", f"${daily_uncached * 30:,.2f}", "0%")
    table.add_row("Có dùng Prompt Caching", f"${daily_cached:.2f}", f"${daily_cached * 30:,.2f}", f"{(1 - daily_cached/daily_uncached)*100:.1f}%")
    console.print(table)
    console.print("[dim]💡 Lưu ý kỹ thuật: Để kích hoạt Cache, đoạn Prompt đầu (System + Tài liệu) phải giống hệt nhau ở mỗi request (Prefix matching).[/dim]")


# =====================================================================
# 3. TRỰC QUAN HÓA STREAMING RESPONSES (TTFT)
# =====================================================================
def demo_streaming_simulation():
    console.print()
    console.print(Panel("[bold green]3. STREAMING RESPONSES & CHỈ SỐ TTFT (Time To First Token)[/bold green]", border_style="magenta"))

    sample_answer = "Streaming giúp hiển thị từng mẩu từ ngay khi mô hình vừa tính toán xong, loại bỏ hoàn toàn cảm giác chờ đợi của người dùng!"
    tokens = sample_answer.split()

    console.print("[cyan]Mô phỏng Streaming token qua Terminal (Zero perceived latency):[/cyan]")
    start_time = time.time()
    first_token_time = None

    for i, token in enumerate(tokens):
        if i == 0:
            time.sleep(0.35) # Giả lập 350ms mạng để tới token đầu tiên
            first_token_time = time.time()
            ttft = (first_token_time - start_time) * 1000
            console.print(f"[dim](TTFT: {ttft:.0f}ms) ➔ [/dim]", end="")
        else:
            time.sleep(0.06) # Giả lập tốc độ sinh token 15-20 token/giây
        
        sys.stdout.write(token + " ")
        sys.stdout.flush()

    total_time = time.time() - start_time
    console.print(f"\n\n[bold green]✓ Hoàn thành trong {total_time:.2f}s[/bold green]")


if __name__ == "__main__":
    demo_function_calling()
    demo_prompt_caching()
    demo_streaming_simulation()
