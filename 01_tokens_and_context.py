"""
01_tokens_and_context.py
------------------------
BƯỚC 2: CORE LLM ELEMENTS - TOKENS & CONTEXT WINDOW

Kiến thức thực hành:
1. Tokenization là gì? Trực quan hóa cách LLM chia nhỏ văn bản thành các token ID.
2. Tại sao Tiếng Việt lại tốn nhiều token hơn Tiếng Anh?
3. Mô phỏng cấu trúc Context Window trong một ứng dụng thực tế.
4. Cách tính toán chi phí (Token Pricing).
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
from rich.table import Table
from rich.panel import Panel

console = Console(force_terminal=True)

def demo_tokenization():
    console.print(Panel("[bold green]1. TRỰC QUAN HÓA TOKENIZATION (BPE Tokenizer - GPT-4o / Modern LLMs)[/bold green]", border_style="cyan"))
    
    # Sử dụng bộ mã hóa o200k_base (bộ tokenizer mới nhất của GPT-4o)
    encoding = tiktoken.get_encoding("o200k_base")
    
    sample_en = "AI Engineering is amazing!"
    sample_vi = "Học AI Engineering rất thú vị!"
    
    # Mã hóa thành danh sách Token IDs
    tokens_en = encoding.encode(sample_en)
    tokens_vi = encoding.encode(sample_vi)
    
    # Giải mã từng token để xem từng mẩu từ
    decoded_en = [encoding.decode([t]) for t in tokens_en]
    decoded_vi = [encoding.decode([t]) for t in tokens_vi]
    
    table = Table(title="So sánh Tokenization: Tiếng Anh vs Tiếng Việt")
    table.add_column("Ngôn ngữ", style="bold")
    table.add_column("Văn bản gốc", style="white")
    table.add_column("Số từ", justify="right")
    table.add_column("Số Tokens", justify="right", style="bold magenta")
    table.add_column("Các mẩu Tokens được tách ra", style="yellow")
    
    table.add_row(
        "Tiếng Anh",
        sample_en,
        str(len(sample_en.split())),
        str(len(tokens_en)),
        str(decoded_en)
    )
    table.add_row(
        "Tiếng Việt",
        sample_vi,
        str(len(sample_vi.split())),
        str(len(tokens_vi)),
        str(decoded_vi)
    )
    console.print(table)
    console.print("[italic dim]💡 Lưu ý: Các ký tự có dấu như 'ọ', 'ấ', 'ị' thường bị chia thành nhiều mảnh byte nhỏ, khiến số token tiếng Việt cao hơn.[/italic dim]\n")

def demo_context_window_budget():
    console.print(Panel("[bold green]2. MÔ PHỎNG PHÂN BỔ CONTEXT WINDOW TRONG MỘT HỆ THỐNG RAG[/bold green]", border_style="cyan"))
    
    context_limit = 8192 # Ví dụ model có 8k context
    
    system_prompt_tokens = 500      # Định hình luật lệ, persona
    rag_documents_tokens = 4500     # Dữ liệu từ 3 trang PDF tìm được
    chat_history_tokens = 1800      # Lịch sử 5 lượt chat trước đó
    user_query_tokens = 150         # Câu hỏi hiện tại của người dùng
    
    total_input_tokens = system_prompt_tokens + rag_documents_tokens + chat_history_tokens + user_query_tokens
    remaining_budget_for_output = context_limit - total_input_tokens
    
    table = Table(title=f"Phân bổ Context Window (Giới hạn: {context_limit:,} Tokens)")
    table.add_column("Thành phần trong Context", style="bold cyan")
    table.add_column("Số Tokens", justify="right")
    table.add_column("Tỷ lệ chiếm dụng (%)", justify="right", style="magenta")
    
    components = [
        ("System Prompt (Chỉ dẫn hệ thống)", system_prompt_tokens),
        ("RAG Retrieved Context (Tài liệu PDF)", rag_documents_tokens),
        ("Chat History (Lịch sử hội thoại)", chat_history_tokens),
        ("User Query (Câu hỏi mới)", user_query_tokens),
    ]
    
    for name, tokens in components:
        percentage = (tokens / context_limit) * 100
        table.add_row(name, f"{tokens:,}", f"{percentage:.1f}%")
        
    table.add_row(
        "[bold green]TỔNG INPUT TOKENS[/bold green]",
        f"[bold green]{total_input_tokens:,}[/bold green]",
        f"[bold green]{(total_input_tokens/context_limit)*100:.1f}%[/bold green]"
    )
    table.add_row(
        "[bold yellow]Dung lượng còn lại cho AI trả lời (Output Budget)[/bold yellow]",
        f"[bold yellow]{remaining_budget_for_output:,}[/bold yellow]",
        f"[bold yellow]{(remaining_budget_for_output/context_limit)*100:.1f}%[/bold yellow]"
    )
    
    console.print(table)
    if remaining_budget_for_output < 500:
        console.print("[bold red]⚠️ Cảnh báo: Context sắp cạn! Cần tóm tắt lịch sử chat (Summary) hoặc giảm chunk RAG.[/bold red]")
    else:
        console.print("[green]✓ Context an toàn, AI còn đủ chỗ để sinh ra câu trả lời chi tiết.[/green]\n")

if __name__ == "__main__":
    demo_tokenization()
    demo_context_window_budget()
