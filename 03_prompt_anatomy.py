"""
03_prompt_anatomy.py
--------------------
BƯỚC THỰC HÀNH: PROMPT ANATOMY & STRUCTURED OUTPUT
Bám sát lộ trình roadmap.sh/ai-engineer -> Prompt Engineering:
1. Input Format (Delimiters, Role tagging)
2. System Prompting
3. Role & Behavior
4. Context
5. Constraint
6. Structured Output (Pydantic Schema)
"""

import io
import sys
from typing import List, Optional
from pydantic import BaseModel, Field

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
# THÀNH PHẦN 6: STRUCTURED OUTPUT SCHEMA (Định nghĩa khuôn mẫu dữ liệu)
# =====================================================================
class RiskItem(BaseModel):
    risk_title: str = Field(description="Tên ngắn gọn của rủi ro")
    severity: str = Field(description="Mức độ nghiêm trọng: THẤP, TRUNG BÌNH, CAO")
    mitigation: str = Field(description="Giải pháp khắc phục đề xuất")

class ContractAnalysisResult(BaseModel):
    contract_title: str = Field(description="Tiêu đề hoặc loại hợp đồng")
    parties_involved: List[str] = Field(description="Danh sách các bên tham gia ký kết")
    total_value_vnd: Optional[float] = Field(None, description="Tổng giá trị hợp đồng bằng VNĐ nếu có")
    payment_terms: str = Field(description="Tóm tắt điều khoản thanh toán")
    risks_identified: List[RiskItem] = Field(description="Danh sách các rủi ro pháp lý/tài chính được phát hiện")
    overall_verdict: str = Field(description="Đánh giá tổng quan: CHẤP THUẬN, CẦN ĐÀM PHÁN LẠI, hoặc TỪ CHỐI")


# =====================================================================
# THÀNH PHẦN 1 ĐẾN 5: PROMPT BUILDER (Lắp ráp 5 thành phần còn lại)
# =====================================================================
class ProductionPromptBuilder:
    def __init__(self):
        self.role = ""
        self.system_instructions = []
        self.constraints = []
        self.context = ""
        self.task = ""

    def set_role_and_behavior(self, role_description: str):
        self.role = role_description
        return self

    def add_system_instruction(self, instruction: str):
        self.system_instructions.append(instruction)
        return self

    def add_constraint(self, constraint: str):
        self.constraints.append(constraint)
        return self

    def set_context(self, context_data: str):
        self.context = context_data
        return self

    def set_task(self, task_description: str):
        self.task = task_description
        return self

    def build_system_prompt(self) -> str:
        """Lắp ráp System Prompt hoàn chỉnh"""
        parts = []
        if self.role:
            parts.append(f"### VAI TRÒ & PHONG CÁCH:\n{self.role}")
        
        if self.system_instructions:
            inst_text = "\n".join(f"- {inst}" for inst in self.system_instructions)
            parts.append(f"### NGUYÊN TẮC HỆ THỐNG CỐT LÕI:\n{inst_text}")

        if self.constraints:
            const_text = "\n".join(f"- {c}" for c in self.constraints)
            parts.append(f"### RÀNG BUỘC NGHIÊM NGẶT (CONSTRAINTS):\n{const_text}")

        return "\n\n".join(parts)

    def build_user_prompt(self) -> str:
        """Lắp ráp User Prompt có phân tách ngữ cảnh (Delimiters)"""
        parts = []
        if self.context:
            parts.append(f"<context_documents>\n{self.context.strip()}\n</context_documents>")
        
        parts.append(f"<task_instruction>\n{self.task.strip()}\n</task_instruction>")
        return "\n\n".join(parts)


def run_demo():
    console.print(Panel(
        "[bold green]MINH HỌA GIẢI PHẪU PROMPT (PROMPT ANATOMY) TRONG HỆ THỐNG PHÂN TÍCH HỢP ĐỒNG[/bold green]",
        border_style="cyan"
    ))

    # Dữ liệu ngữ cảnh giả lập từ hệ thống RAG (1 trang hợp đồng dịch vụ)
    sample_contract_text = """
    HỢP ĐỒNG DỊCH VỤ PHÁT TRIỂN PHẦN MỀM
    Bên A: Công ty Cổ phần Công nghệ Alpha (Bên thuê)
    Bên B: Công ty TNHH Phần mềm Beta (Bên cung cấp)
    Điều 3: Giá trị hợp đồng và thanh toán
    - Tổng giá trị hợp đồng là 500,000,000 VNĐ (Năm trăm triệu đồng chẵn), chưa bao gồm thuế VAT.
    - Bên A sẽ tạm ứng 20% ngay sau khi ký hợp đồng. 80% còn lại sẽ thanh toán sau 90 ngày kể từ ngày nghiệm thu toàn bộ.
    Điều 7: Phạt vi phạm
    - Nếu Bên B giao trễ hạn quá 3 ngày, Bên B phải bồi thường 100% giá trị hợp đồng và chịu toàn bộ thiệt hại phát sinh.
    - Bên A có quyền đơn phương chấm dứt hợp đồng bất kỳ lúc nào mà không cần báo trước và không phải bồi thường bất kỳ chi phí nào.
    """

    # Lắp ráp Prompt theo đúng chuẩn Prompt Anatomy
    builder = (
        ProductionPromptBuilder()
        # 1. Role & Behavior
        .set_role_and_behavior(
            "Bạn là một Luật sư Trưởng chuyên gia về thẩm định rủi ro hợp đồng kinh tế và dịch vụ công nghệ thông tin. "
            "Phong cách của bạn sắc bén, cẩn trọng và luôn bảo vệ tối đa lợi ích hợp pháp của khách hàng."
        )
        # 2. System Prompting
        .add_system_instruction("Luôn kiểm tra kỹ các điều khoản bất cân xứng, thời hạn thanh toán kéo dài và mức phạt vi phạm bất hợp lý.")
        .add_system_instruction("Nếu điều khoản nào có lợi thế tuyệt đối cho một bên, bắt buộc phải cảnh báo ở mức độ CAO.")
        # 3. Constraints
        .add_constraint("Chỉ phân tích nội dung được cung cấp bên trong thẻ <context_documents>.")
        .add_constraint("Tuyệt đối KHÔNG tự sáng tác thêm các điều khoản không có trong văn bản.")
        .add_constraint("Đầu ra bắt buộc phải tuân thủ chính xác Schema JSON đã quy định, không kèm bất kỳ lời chào hỏi mở đầu.")
        # 4. Context (Dữ liệu đưa vào)
        .set_context(sample_contract_text)
        # 5. Task
        .set_task("Hãy rà soát toàn bộ hợp đồng trên, bóc tách các thực thể chính và chỉ ra các rủi ro pháp lý lớn nhất.")
    )

    system_prompt = builder.build_system_prompt()
    user_prompt = builder.build_user_prompt()

    # Hiển thị giải phẫu của System Prompt
    console.print(Panel(system_prompt, title="[bold yellow]1. SYSTEM PROMPT (Role, Behavior, Constraints)[/bold yellow]", border_style="yellow"))
    
    # Hiển thị giải phẫu của User Prompt (Có Delimiters phân tách rõ ràng)
    console.print(Panel(user_prompt, title="[bold cyan]2. USER PROMPT (Context Delimiters & Task)[/bold cyan]", border_style="blue"))

    # Hiển thị JSON Schema tạo từ Pydantic (Structured Output)
    schema_json = ContractAnalysisResult.model_json_schema()
    console.print(Panel(
        f"[bold magenta]Pydantic Model:[/bold magenta] ContractAnalysisResult\n"
        f"[bold cyan]Các trường bắt buộc:[/bold cyan] {', '.join(schema_json.get('required', []))}\n"
        f"[bold green]Mục tiêu:[/bold green] Buộc LLM chỉ được trả về đúng định dạng này để nạp thẳng vào Database.",
        title="[bold green]3. STRUCTURED OUTPUT (Pydantic Schema Enforcement)[/bold green]",
        border_style="green"
    ))

    # Mô phỏng dữ liệu JSON chuẩn mà LLM trả về sau khi parse vào Pydantic
    mock_llm_json_response = {
        "contract_title": "Hợp đồng dịch vụ phát triển phần mềm",
        "parties_involved": ["Công ty Cổ phần Công nghệ Alpha", "Công ty TNHH Phần mềm Beta"],
        "total_value_vnd": 500000000.0,
        "payment_terms": "Tạm ứng 20% khi ký, 80% còn lại sau 90 ngày kể từ nghiệm thu (rất dài).",
        "risks_identified": [
            {
                "risk_title": "Thời hạn thanh toán bất lợi",
                "severity": "CAO",
                "mitigation": "Đàm phán rút ngắn thời hạn thanh toán 80% còn lại xuống 15-30 ngày thay vì 90 ngày."
            },
            {
                "risk_title": "Phạt trễ hạn 100% giá trị hợp đồng",
                "severity": "CAO",
                "mitigation": "Điều chỉnh mức phạt vi phạm theo luật thương mại (tối đa 8% phần nghĩa vụ bị vi phạm)."
            },
            {
                "risk_title": "Bên A đơn phương chấm dứt hợp đồng không cần báo trước",
                "severity": "CAO",
                "mitigation": "Bổ sung điều khoản phải thông báo trước ít nhất 30 ngày và thanh toán các khối lượng công việc đã hoàn thành."
            }
        ],
        "overall_verdict": "CẦN ĐÀM PHÁN LẠI"
    }

    # Validate bằng Pydantic
    validated_result = ContractAnalysisResult.model_validate(mock_llm_json_response)
    
    table = Table(title="4. KẾT QUẢ ĐÃ ĐƯỢC VALIDATE BỞI PYDANTIC (Sẵn sàng nạp vào DB)")
    table.add_column("Trường", style="bold cyan")
    table.add_column("Dữ liệu bóc tách được", style="white")

    table.add_row("Loại hợp đồng", validated_result.contract_title)
    table.add_row("Các bên tham gia", ", ".join(validated_result.parties_involved))
    table.add_row("Giá trị (VNĐ)", f"{validated_result.total_value_vnd:,.0f} VNĐ")
    table.add_row("Điều khoản thanh toán", validated_result.payment_terms)
    table.add_row("Phán quyết", f"[bold red]{validated_result.overall_verdict}[/bold red]")
    console.print(table)

    console.print("\n[bold magenta]Chi tiết các rủi ro đã bóc tách:[/bold magenta]")
    for r in validated_result.risks_identified:
        console.print(f"  ⚠️ [bold red][{r.severity}][/bold red] [bold]{r.risk_title}[/bold]")
        console.print(f"     👉 Khắc phục: [italic]{r.mitigation}[/italic]\n")

if __name__ == "__main__":
    run_demo()
