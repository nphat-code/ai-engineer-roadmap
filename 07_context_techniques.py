"""
07_context_techniques.py
------------------------
BƯỚC THỰC HÀNH: CONTEXT ENGINEERING TECHNIQUES
Bám sát lộ trình roadmap.sh/ai-engineer -> Context Engineering:
1. Memory Systems (Sliding Buffer vs Summary Memory)
2. Context Compaction (Kỹ thuật nén token)
3. Long-Context Processing & "Lost in the Middle"
4. Multi-agent Context Isolation vs Sharing
"""

import io
import sys
import tiktoken

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

    # Giả sử qua 10 lượt hội thoại, lịch sử chat gốc rất dài:
    raw_chat_history = [
        ("User", "Chào bot, tôi tên là Tuấn, lập trình viên Backend ở Hà Nội."),
        ("AI", "Chào anh Tuấn! Rất vui được hỗ trợ anh về các chủ đề Backend."),
        ("User", "Hôm nay tôi muốn tìm hiểu về cơ sở dữ liệu phân tán."),
        ("AI", "Dạ vâng, cơ sở dữ liệu phân tán chia làm SQL phân tán (như CockroachDB) và NoSQL (như Cassandra)..."),
        ("User", "Tôi chọn PostgreSQL kết hợp Citus extension."),
        ("AI", "Citus extension là giải pháp sharding tuyệt vời cho PostgreSQL..."),
        ("User", "Tôi đã cấu hình 3 nodes worker và 1 coordinator."),
        ("AI", "Tuyệt vời, anh cần kiểm tra cấu hình mạng và replication factor..."),
        ("User", "Bây giờ tôi muốn viết script backup tự động thì làm thế nào?")
    ]

    # Cách 1: Sliding Window Buffer (Chỉ giữ 2 lượt gần nhất) -> Quên mất tên User và bối cảnh Citus!
    sliding_window = raw_chat_history[-2:]

    # Cách 2: Summary Memory (Tóm tắt các lượt cũ + giữ 2 lượt mới)
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

    # Sau khi AI đã quan sát xong, tầng Context Compaction nén dữ liệu này trước khi chuyển sang lượt tiếp theo:
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
# 4. MULTI-AGENT CONTEXT ISOLATION
# =====================================================================
def demo_context_isolation():
    console.print()
    console.print(Panel("[bold green]4. MULTI-AGENT CONTEXT SHARING VS CONTEXT ISOLATION[/bold green]", border_style="cyan"))

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


if __name__ == "__main__":
    demo_memory_systems()
    demo_context_compaction()
    demo_lost_in_the_middle()
    demo_context_isolation()
