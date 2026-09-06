"""
08_context_warehouses.py
------------------------
BƯỚC THỰC HÀNH: TOOLS & CONTEXT WAREHOUSES
Bám sát lộ trình roadmap.sh/ai-engineer -> Context Engineering:
1. Atlan & DataHub (Active Metadata Catalog & Business Glossary Context)
2. PostHog (User Telemetry & Live Behavioral Context)
3. Modus (Ultra-low latency Wasm API data connector)
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
# 1. ATLAN / DATAHUB (METADATA CATALOG & BUSINESS GLOSSARY)
# =====================================================================
class MockDataCatalog:
    """Mô phỏng Atlan / DataHub: Cung cấp định nghĩa nghiệp vụ và Schema cho AI"""

    def get_business_term(self, term: str) -> str:
        glossary = {
            "churn_rate": (
                "Định nghĩa chuẩn nội bộ: Tỷ lệ người dùng trả phí không có bất kỳ "
                "hoạt động đăng nhập nào trong vòng liên tục 45 ngày."
            ),
            "mrr": "Monthly Recurring Revenue: Doanh thu định kỳ hàng tháng từ các gói thuê bao hoạt động."
        }
        return glossary.get(term, "Không tìm thấy định nghĩa thuật ngữ.")

    def get_table_schema(self, table_name: str) -> Dict[str, str]:
        schemas = {
            "dim_subscriptions": {
                "user_id": "VARCHAR(50) - Mã định danh khách hàng",
                "plan_type": "VARCHAR(20) - Loại gói: Free, Pro, Enterprise",
                "last_active_at": "TIMESTAMP - Thời điểm tương tác cuối cùng",
                "status": "VARCHAR(20) - Trạng thái: active, canceled, paused"
            }
        }
        return schemas.get(table_name, {})


# =====================================================================
# 2. POSTHOG (LIVE USER TELEMETRY & FEATURE FLAGS)
# =====================================================================
class MockPostHog:
    """Mô phỏng PostHog: Cung cấp ngữ cảnh hành vi người dùng thời gian thực"""

    def get_user_session_context(self, user_id: str) -> Dict[str, Any]:
        return {
            "user_id": user_id,
            "current_page": "/dashboard/billing",
            "last_action": "click_upgrade_button",
            "feature_flags": {"new_pricing_v2": True, "ai_assistant_beta": True},
            "recent_errors": ["PaymentMethodFailed: Card expired (error_code: 402)"]
        }


# =====================================================================
# 3. MODUS (FAST CONTEXT INGESTION PIPELINE)
# =====================================================================
class ModusContextPipeline:
    """
    Mô phỏng Modus Framework:
    Tầng trung gian Wasm kết nối siêu tốc giữa Data Catalog, Telemetry và LLM
    """
    def __init__(self):
        self.catalog = MockDataCatalog()
        self.posthog = MockPostHog()

    def assemble_enterprise_context(self, user_id: str, query: str) -> Dict[str, Any]:
        # 1. Kéo ngữ cảnh nghiệp vụ từ Data Catalog (Atlan/DataHub)
        glossary_context = self.catalog.get_business_term("churn_rate")
        schema_context = self.catalog.get_table_schema("dim_subscriptions")

        # 2. Kéo ngữ cảnh hành vi từ Product Analytics (PostHog)
        user_telemetry = self.posthog.get_user_session_context(user_id)

        # 3. Đóng gói thành Context Layer hoàn chỉnh
        return {
            "business_definition": glossary_context,
            "database_schema": schema_context,
            "user_telemetry": user_telemetry,
            "user_query": query
        }


def run_demo():
    console.print(Panel(
        "[bold green]MINH HỌA ENTERPRISE CONTEXT WAREHOUSES: ATLAN, DATAHUB, POSTHOG & MODUS[/bold green]",
        border_style="cyan"
    ))

    pipeline = ModusContextPipeline()
    user_id = "usr_vip_999"
    user_query = "Tôi đang ở trang thanh toán nhưng không nâng cấp gói được, bot kiểm tra giúp tôi?"

    console.print(f"[bold cyan]Người dùng ({user_id}) hỏi:[/bold cyan] '{user_query}'\n")

    # Kéo ngữ cảnh tự động qua Modus
    context = pipeline.assemble_enterprise_context(user_id=user_id, query=user_query)

    # Hiển thị bảng tổng hợp các nguồn Context
    table = Table(title="Các mảnh ghép Context được kéo tự động từ Doanh nghiệp")
    table.add_column("Hệ thống nguồn", style="bold cyan")
    table.add_column("Loại ngữ cảnh (Context Type)", style="yellow")
    table.add_column("Dữ liệu cụ thể được nạp vào LLM", style="white")

    table.add_row(
        "PostHog",
        "Live User Telemetry & Error Logs",
        f"Màn hình: {context['user_telemetry']['current_page']}\n"
        f"Lỗi gần nhất: [bold red]{context['user_telemetry']['recent_errors'][0]}[/bold red]\n"
        f"Feature Flag: {context['user_telemetry']['feature_flags']}"
    )

    table.add_row(
        "Atlan / DataHub",
        "Business Glossary & Catalog",
        f"Định nghĩa Churn: {context['business_definition']}\n"
        f"Schema bảng liên quan: dim_subscriptions ({len(context['database_schema'])} cột)"
    )

    console.print(table)

    # Câu trả lời của AI nhờ có Context Warehouse
    ai_response = """
    Chào bạn! Tôi thấy bạn đang ở trang **Thanh toán (/dashboard/billing)** và vừa gặp lỗi 
    thẻ thanh toán bị hết hạn (**PaymentMethodFailed - Card expired**). 
    
    👉 Bạn vui lòng cập nhật lại ngày hết hạn hoặc đổi phương thức thanh toán mới để tiếp tục 
    kích hoạt gói **Pro/Enterprise** nhé! Tôi đã giữ nguyên ưu đãi gói cước mới (Pricing v2) cho tài khoản của bạn.
    """

    console.print(Panel(
        ai_response.strip(),
        title="🤖 Câu trả lời siêu chuẩn xác của AI (Nhờ có đầy đủ Context từ PostHog & Catalog)",
        border_style="green"
    ))
    console.print(
        "[dim]💡 AI Engineer Insight: Nếu không có PostHog cấp telemetry context, AI sẽ phải hỏi lại: "
        "'Bạn gặp lỗi gì, chụp màn hình gửi tôi xem?'. "
        "Context Warehouses giúp AI hiểu sự việc trước cả khi người dùng giải thích![/dim]"
    )


if __name__ == "__main__":
    run_demo()
