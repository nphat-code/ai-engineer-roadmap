# 🚀 AI Engineer Roadmap - Hands-on Learning Journey

Repository này ghi lại toàn bộ lộ trình học tập và thực hành bài bản theo **[roadmap.sh/ai-engineer](https://roadmap.sh/ai-engineer)**.

---

## 📂 Danh mục bài thực hành

| Bài học | Chủ đề trên Roadmap | Nội dung cốt lõi |
| :--- | :--- | :--- |
| [01_tokens_and_context.py](file:///c:/Study/AI/01_tokens_and_context.py) | **Core Elements: Tokens & Context** | • Trực quan hóa BPE Tokenizer (so sánh tiếng Anh vs tiếng Việt).<br>• Phân bổ Context Window Budget trong ứng dụng RAG thực tế.<br>• Tính toán chi phí API (Pricing). |
| [02_sampling_parameters.py](file:///c:/Study/AI/02_sampling_parameters.py) | **Core Elements: Sampling Parameters** | • Mô phỏng toán học Next-Token Prediction & Softmax.<br>• Tác động của **Temperature** ($0.1 \to 1.5$).<br>• Cơ chế lọc an toàn: **Top-K** vs **Top-P (Nucleus)**.<br>• Chống lặp từ: **Frequency Penalty** & **Presence Penalty**. |
| [03_prompt_anatomy.py](file:///c:/Study/AI/03_prompt_anatomy.py) | **Prompt Engineering: Prompt Anatomy** | • Giải phẫu 6 thành phần của Prompt chuẩn Production.<br>• Phân tách ngữ cảnh bằng **Delimiters** chống Prompt Injection.<br>• Ép kiểu dữ liệu đầu ra an toàn với **Pydantic Schema (Structured Output)**. |
| [04_prompting_techniques.py](file:///c:/Study/AI/04_prompting_techniques.py) | **Prompt Engineering: Prompting Techniques** | • **Zero-Shot**: Hỏi trực tiếp.<br>• **Few-Shot**: Học qua ví dụ mẫu gán nhãn.<br>• **Chain-of-Thought (CoT)**: Dẫn dắt suy luận từng bước.<br>• **ReAct**: Vòng lặp *Thought ➔ Action ➔ Observation* (nền tảng của AI Agents). |

---

## 🛠️ Cài đặt & Chạy thử nghiệm

### 1. Khởi tạo môi trường ảo
```powershell
# Tạo môi trường ảo
python -m venv .venv

# Kích hoạt môi trường (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Cài đặt các thư viện cần thiết
pip install tiktoken pydantic rich python-dotenv google-genai openai
```

### 2. Chạy các bài thực hành
```powershell
# Bài 1: Tokens & Context Window
python 01_tokens_and_context.py

# Bài 2: Sampling Parameters
python 02_sampling_parameters.py

# Bài 3: Prompt Anatomy & Structured Output
python 03_prompt_anatomy.py

# Bài 4: Prompting Techniques (Zero-shot, Few-shot, CoT, ReAct)
python 04_prompting_techniques.py
```
