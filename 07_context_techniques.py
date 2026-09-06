"""
07_context_techniques.py
------------------------
BƯỚC THỰC HÀNH: CONTEXT ENGINEERING TECHNIQUES
Bám sát lộ trình roadmap.sh/ai-engineer -> Context Engineering:
1. Memory Systems (Sliding Buffer vs Summary Memory)
2. Context Compaction (Kỹ thuật nén token)
3. Long-Context Processing & "Lost in the Middle"
4. Stale & Historical Context (Xử lý dữ liệu lỗi thời & State Tracking)
5. Multi-agent Context Isolation vs Sharing
6. Context Failure Modes (4 chế độ hỏng hóc ngữ cảnh)
"""

import io
import sys
import tiktoken
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
encoding = tiktoken.get_encoding("o200k_base")

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

# =====================================================================
# 1. MEMORY SYSTEMS (BUFFER VS SUMMARY MEMORY)
# =====================================================================
def demo_memory_systems():
    console.print(Panel("[bold green]1. MEMORY SYSTEMS: SLIDING WINDOW BUFFER VS SUMMARY MEMORY[/bold green]", border_style="cyan"))

    raw_chat_history = [
        ("User", "Chào bot, tôi tên là Tuấn, lập trình viên Backend ở Hà Nội."),
        ("AI", "Chào anh Tuấn! Rất vui được hỗ trợ anh về các chủ đề Backend."),
        ("User", "Hôm nay tôi muốn tìm hiểu về cơ sở dữ liệu phân tán."),
        ("AI", "Dạ vâng, cơ sở dữ liệu phân tán chia làm SQL phân tán và NoSQL..."),
        ("User", "Tôi chọn PostgreSQL kết hợp Citus extension."),
        ("AI", "Citus extension là giải pháp sharding tuyệt vời cho PostgreSQL..."),
        ("User", "Tôi đã cấu hình 3 nodes worker và 1 coordinator."),
        ("AI", "Tuyệt vời, anh cần kiểm tra cấu hình mạng và replication factor..."),
        ("User", "Bây giờ tôi muốn viết script backup tự động thì làm thế nào?")
    ]

    sliding_window = raw_chat_history[-2:]
    summary_of_past = "Người dùng tên Tuấn, Backend Dev tại Hà Nội. Đang triển khai PostgreSQL + Citus (3 workers, 1 coordinator)."

    table = Table(title="So sánh cơ chế lưu trữ bộ nhớ")
    table.add_column("Cơ chế", style="bold cyan")
    table.add_column("Nội dung đưa vào Context", style="white")
    table.add_column("Ưu / Nhược điểm", style="dim yellow")

    table.add_row(
        "Raw History (Lưu tất cả)",
        f"{len(raw_chat_history)} tin nhắn nguyên văn",
        "❌ Tốn token tăng dần đều theo thời gian, nhanh chạm trần Context."
    )
    table.add_row(
        "Sliding Window (Chỉ lấy 2 tin cuối)",
        f"{sliding_window[0][0]}: {sliding_window[0][1]}\n{sliding_window[1][0]}: {sliding_window[1][1]}",
        "⚠️ Tiết kiệm token nhưng 'mất trí nhớ': Quên mất tên Tuấn và bối cảnh Citus."
    )
    table.add_row(
        "Summary Memory (Tóm tắt + Tin mới)",
        f"[Summary]: {summary_of_past}\n[Latest]: {sliding_window[1][1]}",
        "✅ Hoàn hảo: Tiết kiệm 70% token mà vẫn nhớ trọn vẹn thông tin cốt lõi!"
    )
    console.print(table)


# =====================================================================
# 2. CONTEXT COMPACTION (NÉN NGỮ CẢNH)
# =====================================================================
def demo_context_compaction():
    console.print()
    console.print(Panel("[bold green]2. CONTEXT COMPACTION (Kỹ thuật nén và cắt tỉa ngữ cảnh thừa)[/bold green]", border_style="yellow"))

    raw_tool_output = """
    HTTP/1.1 200 OK
    Date: Sun, 06 Sep 2026 10:00:00 GMT
    Server: Apache/2.4.41 (Ubuntu)
    Content-Type: application/json; charset=utf-8
    Connection: keep-alive
    [
        {"id": 1, "name": "Sản phẩm A", "price": 100000, "in_stock": true, "created_at": "2025-01-01", "internal_hash": "a1b2c3d4e5"},
        {"id": 2, "name": "Sản phẩm B", "price": 250000, "in_stock": false, "created_at": "2025-01-02", "internal_hash": "f6g7h8i9j0"}
    ]
    """

    compacted_output = "Sản phẩm A: 100k (Còn hàng); Sản phẩm B: 250k (Hết hàng)"
    tokens_before = count_tokens(raw_tool_output)
    tokens_after = count_tokens(compacted_output)
    saved_percent = (1 - tokens_after / tokens_before) * 100

    table = Table(title="Kết quả nén ngữ cảnh (Context Compaction)")
    table.add_column("Dạng dữ liệu", style="bold")
    table.add_column("Nội dung", style="white")
    table.add_column("Số Tokens", justify="right", style="bold magenta")

    table.add_row("Dữ liệu thô ban đầu (Raw Tool Output)", raw_tool_output.strip()[:100] + "... [cắt bớt]", str(tokens_before))
    table.add_row("Dữ liệu đã nén (Compacted Fact)", compacted_output, str(tokens_after))
    console.print(table)
    console.print(f"[bold green]➔ Tiết kiệm được {saved_percent:.1f}% dung lượng Token mà không mất thông tin quan trọng![/bold green]")


# =====================================================================
# 3. LONG-CONTEXT & "LOST IN THE MIDDLE"
# =====================================================================
def demo_lost_in_the_middle():
    console.print()
    console.print(Panel("[bold green]3. HIỆN TƯỢNG 'LOST IN THE MIDDLE' TRONG NGỮ CẢNH DÀI[/bold green]", border_style="magenta"))

    diagram = """
    Mức độ tập trung chú ý (Attention Weight) của mô hình Transformer theo vị trí tài liệu:

    Độ chú ý
      100% ──┐                                         ┌── 100%
             │  Đầu ngữ cảnh             Cuối ngữ cảnh │
             │  (Primacy Effect)       (Recency Effect)│
             │       \                               / │
        30% ──┤        \                             /  ├── 30%
             │         \      VÙNG NGUY HIỂM       /   │
             │          └─────── (BỊ BỎ QUÊN) ────┘    │
        0% ──┴─────────────────────────────────────────┴── 0%
            Vị trí 0% (Đầu)     Vị trí 50% (Giữa)   Vị trí 100% (Cuối)
    """
    console.print(Panel(diagram, title="Đồ thị hình chữ U của sự chú ý (U-shaped Attention Curve)", border_style="blue"))
    console.print(
        "[bold yellow]💡 Quy tắc vàng cho AI Engineer:[/bold yellow]\n"
        "• [green]NÊN:[/green] Đặt chỉ thị quan trọng (System Rules, Ràng buộc) ở [bold]ĐẦU[/bold] và câu hỏi hiện tại + thông tin chốt ở [bold]CUỐI[/bold].\n"
        "• [red]TRÁNH:[/red] Giấu điều khoản sống còn vào chính giữa hàng chục trang tài liệu RAG."
    )


# =====================================================================
# 4. STALE & HISTORICAL CONTEXT (XỬ LÝ DỮ LIỆU LỖI THỜI & STATE TRACKING)
# =====================================================================
def demo_stale_and_historical_context():
    console.print()
    console.print(Panel("[bold green]4. STALE & HISTORICAL CONTEXT (Xử lý Ngữ cảnh Lỗi thời & State Tracking)[/bold green]", border_style="cyan"))

    # Tình huống: Người dùng đổi ý trong cuộc hội thoại đặt vé máy bay
    table = Table(title="Mô phỏng State Tracking & Invalidation khi User đổi ý")
    table.add_column("Lượt chat (Turn)", style="bold")
    table.add_column("Tin nhắn của User", style="white")
    table.add_column("Trạng thái Context cũ", style="dim red")
    table.add_column("Trạng thái Context mới (Active State)", style="bold green")

    table.add_row(
        "Lượt 1",
        "Tôi muốn đặt 1 vé máy bay đi Đà Nẵng sáng mai.",
        "Chưa có",
        "{destination: 'Đà Nẵng', departure: 'Sáng mai'}"
    )
    table.add_row(
        "Lượt 2",
        "Có chuyến nào của Vietnam Airlines không bạn?",
        "{destination: 'Đà Nẵng'}",
        "{destination: 'Đà Nẵng', airline: 'Vietnam Airlines'}"
    )
    table.add_row(
        "Lượt 3 (Đổi ý)",
        "Khoan đã! Tôi hủy chuyến Đà Nẵng, đổi sang đi Đà Lạt chiều mai nhé.",
        "[STALE]: destination: 'Đà Nẵng'\n(Cũ - Phải vô hiệu hóa)",
        "✅ [ACTIVE]: destination: 'Đà Lạt', departure: 'Chiều mai'\n(Đã ghi đè thành công)"
    )
    console.print(table)
    console.print(
        "[dim]💡 AI Engineer Insight: Nếu không có bộ State Tracker gạch bỏ thông tin cũ (Invalidation), "
        "LLM rất dễ bị 'lú' và xác nhận nhầm vé máy bay đi Đà Nẵng cho khách hàng.[/dim]"
    )


# =====================================================================
# 5. MULTI-AGENT CONTEXT ISOLATION
# =====================================================================
def demo_context_isolation():
    console.print()
    console.print(Panel("[bold green]5. MULTI-AGENT CONTEXT SHARING VS CONTEXT ISOLATION[/bold green]", border_style="yellow"))

    table = Table(title="Mô hình ngữ cảnh trong hệ thống Đa Agent (Multi-Agent)")
    table.add_column("Mô hình", style="bold")
    table.add_column("Cách thức hoạt động", style="white")
    table.add_column("Hậu quả / Lợi ích", style="bold yellow")

    table.add_row(
        "Full Context Sharing (Dùng chung)",
        "Agent A, B, C cùng đọc và ghi chung 1 chuỗi tin nhắn duy nhất.",
        "❌ Context bùng nổ kích thước cực nhanh, các Agent bị 'nhiễu' thông tin chuyên môn của nhau."
    )
    table.add_row(
        "Context Isolation (Cách ly)",
        "Mỗi Agent có bộ nhớ riêng. Giao tiếp qua lại chỉ bằng Artifact (bản báo cáo tóm tắt).",
        "✅ Sạch sẽ, không nhiễu, chi phí token tối ưu, từng Agent tập trung 100% vào chuyên môn."
    )
    console.print(table)


# =====================================================================
# 6. CONTEXT FAILURE MODES (CÁC CHẾ ĐỘ HỎNG HÓC CỦA NGỮ CẢNH)
# =====================================================================
def demo_context_failure_modes():
    console.print()
    console.print(Panel("[bold red]6. CONTEXT FAILURE MODES (4 'Bệnh' Kinh Điển của Ngữ Cảnh)[/bold red]", border_style="red"))

    table = Table(title="Bảng phân loại Context Failure Modes")
    table.add_column("Chế độ hỏng (Failure Mode)", style="bold red")
    table.add_column("Hiện tượng thực tế", style="white")
    table.add_column("Giải pháp của AI Engineer", style="green")

    table.add_row(
        "1. Distraction (Phân tâm)",
        "RAG nhồi quá nhiều đoạn văn không liên quan, khiến AI trả lời lan man, lạc đề.",
        "Dùng Reranker (Cross-encoder) để lọc gắt gao Top-3 tài liệu phù hợp nhất."
    )
    table.add_row(
        "2. Overcrowding (Quá tải)",
        "Cố nhét kín 100% Context Window khiến Attention bị phân tán, suy luận logic kém hẳn.",
        "Đặt trần ngân sách Token (Token Budgeting) tối đa 70% Context Window."
    )
    table.add_row(
        "3. Context Clash (Xung đột)",
        "Hai tài liệu trong ngữ cảnh có số liệu mâu thuẫn nhau -> AI bịa đặt (Hallucination).",
        "Đánh dấu phiên bản dữ liệu (Data Versioning) và ưu tiên tài liệu có timestamp mới nhất."
    )
    table.add_row(
        "4. Positional Bias (Thiên kiến vị trí)",
        "Thông tin quan trọng bị rơi vào vùng giữa Context (Lost in the Middle) và bị bỏ quên.",
        "Sắp xếp lại thứ tự: Thông tin quan trọng nhất đặt ở ĐẦU hoặc CUỐI ngữ cảnh."
    )
    console.print(table)


if __name__ == "__main__":
    demo_memory_systems()
    demo_context_compaction()
    demo_lost_in_the_middle()
    demo_stale_and_historical_context()
    demo_context_isolation()
    demo_context_failure_modes()
