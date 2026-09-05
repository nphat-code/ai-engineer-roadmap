"""
04_prompting_techniques.py
--------------------------
BƯỚC THỰC HÀNH: PROMPTING TECHNIQUES
Bám sát lộ trình roadmap.sh/ai-engineer -> Prompt Engineering:
1. Zero-Shot
2. Few-Shot
3. CoT (Chain-of-Thought)
4. ReAct (Reasoning + Acting - AI Agent foundation)
"""

import io
import sys

if sys.platform == "win32":
    if isinstance(sys.stdout, io.TextIOWrapper):
        sys.stdout.reconfigure(encoding="utf-8")
    if isinstance(sys.stderr, io.TextIOWrapper):
        sys.stderr.reconfigure(encoding="utf-8")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console(force_terminal=True)

def demo_zero_vs_few_shot():
    console.print(Panel("[bold green]1. ZERO-SHOT VS FEW-SHOT (Bài toán: Phân loại ý định khách hàng)[/bold green]", border_style="cyan"))

    # Giả sử quy tắc công ty có 3 nhãn: [KHIEU_NAI, HOI_GIA, KHEN_NGOI]
    # Câu cần phân loại: "App dùng mượt nhưng gói cước hơi chát đấy nhé."

    zero_shot_prompt = """
Hãy phân loại câu sau vào 1 trong 3 nhãn: [KHIEU_NAI, HOI_GIA, KHEN_NGOI]
Câu: "App dùng mượt nhưng gói cước hơi chát đấy nhé."
Nhãn:
"""

    few_shot_prompt = """
Hãy phân loại ý định của câu khách hàng vào 1 trong 3 nhãn: [KHIEU_NAI, HOI_GIA, KHEN_NGOI].

Ví dụ 1:
Câu: "Phần mềm bị lỗi không đăng nhập được từ sáng đến giờ!"
Nhãn: KHIEU_NAI

Ví dụ 2:
Câu: "Cho mình hỏi gói Enterprise 1 năm giá bao nhiêu bạn ơi?"
Nhãn: HOI_GIA

Ví dụ 3:
Câu: "Giao diện bản mới đẹp và mượt hơn hẳn, 5 sao!"
Nhãn: KHEN_NGOI

Ví dụ 4 (Câu mang cả khen lẫn chê về giá -> Quy định công ty ưu tiên xếp vào Khiếu nại dịch vụ/giá):
Câu: "Tính năng thì ổn đấy mà giá cao quá, giảm chút thì tốt."
Nhãn: KHIEU_NAI

Bây giờ hãy phân loại câu sau:
Câu: "App dùng mượt nhưng gói cước hơi chát đấy nhé."
Nhãn:
"""

    table = Table(title="So sánh Zero-Shot vs Few-Shot")
    table.add_column("Đặc điểm", style="bold cyan")
    table.add_column("Zero-Shot", style="yellow")
    table.add_column("Few-Shot", style="green")

    table.add_row(
        "Số ví dụ mẫu cung cấp",
        "0 ví dụ (Chỉ đưa câu hỏi)",
        "2 - 5 ví dụ mẫu (Cặp Input/Output)"
    )
    table.add_row(
        "Khả năng hiểu quy tắc ngầm",
        "Kém: Dễ phân vân giữa KHEN_NGOI và KHIEU_NAI",
        "Xuất sắc: Bắt chước chuẩn xác quy tắc xử lý ca khó từ Ví dụ 4"
    )
    table.add_row(
        "Tiêu tốn Token",
        "Rất ít token đầu vào",
        "Tốn thêm token cho phần ví dụ"
    )
    console.print(table)


def demo_chain_of_thought():
    console.print()
    console.print(Panel("[bold green]2. CHAIN-OF-THOUGHT (CoT - Bài toán suy luận logic/toán)[/bold green]", border_style="yellow"))

    problem = """
Một cửa hàng có 20 quả táo. Buổi sáng bán đi một nửa số táo.
Buổi chiều nhập thêm một số lượng táo bằng đúng số táo còn lại.
Cuối ngày có một khách mua 4 quả và trả lại 1 quả bị dập.
Hỏi cuối ngày cửa hàng còn lại bao nhiêu quả táo?
"""

    # Cách 1: Standard (Zero-Shot) - Bắt trả lời ngay
    standard_prompt = f"""{problem}
Hãy trả về đáp án duy nhất là một con số:
"""

    # Cách 2: CoT - Ép suy luận từng bước
    cot_prompt = f"""{problem}
Hãy giải quyết bài toán trên bằng cách suy nghĩ và diễn giải chi tiết từng bước (Think step by step) trước khi kết luận đáp số.
"""

    mock_standard_output = "Đáp án: 16" # Dễ đoán nhầm do tính nhẩm vội
    mock_cot_output = """
Bước 1: Ban đầu có 20 quả táo.
Bước 2: Buổi sáng bán một nửa -> Đã bán: 20 / 2 = 10 quả. Số táo còn lại: 20 - 10 = 10 quả.
Bước 3: Buổi chiều nhập thêm bằng số táo còn lại -> Nhập thêm: 10 quả. Tổng số táo hiện tại: 10 + 10 = 20 quả.
Bước 4: Khách mua 4 quả -> Còn lại: 20 - 4 = 16 quả.
Bước 5: Khách trả lại 1 quả -> Số táo cuối cùng: 16 + 1 = 17 quả.
===> KẾT LUẬN: Cửa hàng còn lại 17 quả táo.
"""

    console.print(f"[bold cyan]Đề bài:[/bold cyan]{problem}")
    console.print(Panel(mock_standard_output, title="❌ Trả lời trực diện không có CoT (Dễ nhầm lẫn)", border_style="red"))
    console.print(Panel(mock_cot_output.strip(), title="✅ Trả lời qua Chain-of-Thought (Chính xác 100%)", border_style="green"))


def demo_react():
    console.print()
    console.print(Panel("[bold green]3. REACT PATTERN (Reasoning + Acting - Vòng lặp của AI Agent)[/bold green]", border_style="magenta"))

    user_query = "Thời tiết hiện tại ở Đà Nẵng thế nào và với thời tiết đó tôi có nên đi Bà Nà Hills không?"

    react_trace = """
[VÒNG LẶP 1]
- Thought: Người dùng hỏi về thời tiết hiện tại ở Đà Nẵng. Tôi không có dữ liệu thời gian thực vì dữ liệu huấn luyện của tôi bị giới hạn ngày tháng. Tôi cần dùng công cụ tra cứu thời tiết.
- Action: call_weather_api(location="Da Nang")
- Observation: {"temperature": 19, "condition": "Mưa to kéo dài", "wind_kmh": 35, "visibility": "Kém"}

[VÒNG LẶP 2]
- Thought: Đã có thời tiết hiện tại: 19 độ C, mưa to và gió giật 35 km/h. Bây giờ tôi cần suy luận xem điều kiện này có thích hợp đi cáp treo và tham quan ngoài trời tại Bà Nà Hills hay không.
- Reasoning: Bà Nà Hills ở trên núi cao, khi thời tiết mưa to gió lớn sẽ rất lạnh, nhiều sương mù che khuất tầm nhìn Cầu Vàng và cáp treo có thể phải tạm dừng vì gió mạnh.
- Final Answer: Hiện tại Đà Nẵng đang có mưa to, 19°C và gió giật 35 km/h. Bạn KHÔNG NÊN đi Bà Nà Hills hôm nay vì thời tiết trên đỉnh núi sẽ rất lạnh, sương mù dày đặc làm mất tầm nhìn và cáp treo có thể bị gián đoạn do gió lớn.
"""
    console.print(f"[bold cyan]Yêu cầu của User:[/bold cyan] '{user_query}'\n")
    console.print(Panel(react_trace.strip(), title="🤖 Cơ chế hoạt động của ReAct Loop (Thought -> Action -> Observation)", border_style="magenta"))
    console.print("[dim]💡 Nhận xét: ReAct biến LLM từ một 'cuốn từ điển tĩnh' thành một 'thực thể sống' biết tự suy nghĩ và sử dụng công cụ bên ngoài.[/dim]")


if __name__ == "__main__":
    demo_zero_vs_few_shot()
    demo_chain_of_thought()
    demo_react()
