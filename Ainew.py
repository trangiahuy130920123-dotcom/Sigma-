import os
import streamlit as st
import openai
import time

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GitHin Master - Trợ lý AI Cao cấp",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CÀI ĐẶT OPENAI API KEY ---
# Lấy key từ biến môi trường hoặc st.secrets (KHÔNG ghi trực tiếp vào code)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY", "")
if not OPENAI_API_KEY:
    st.error("Chưa có OPENAI_API_KEY. Hãy đặt biến môi trường hoặc thêm vào .streamlit/secrets.toml")
    st.stop()
client = openai.OpenAI(api_key=OPENAI_API_KEY)

# --- TÙY CHỈNH GIAO DIỆN CSS (DARK MODE HIỆN ĐẠI) ---
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #121212;
        color: #e0e0e0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    [data-testid="stSidebar"] {
        background-color: #1e1e1e;
        border-right: 1px solid #333;
    }

    [data-testid="stChatInput"] {
        background-color: #2c2c2c !important;
        color: #fff !important;
        border: 1px solid #444 !important;
        border-radius: 15px !important;
    }

    [data-testid="stChatMessageUser"] {
        background-color: #264653 !important;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
    }
    [data-testid="stChatMessageUser"] .stMarkdown {
        color: #fff !important;
    }

    [data-testid="stChatMessageAssistant"] {
        background-color: #2c2c2c !important;
        border-radius: 15px;
        padding: 15px;
        margin-bottom: 10px;
        border: 1px solid #444;
    }

    h1 { color: #fca311 !important; font-weight: 700 !important; }
    h3 { color: #e0e0e0 !important; }
    
    .stButton button {
        background-color: #fca311;
        color: #121212;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #ffb703;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# --- THANH BÊN (SIDEBAR) ---
with st.sidebar:
    st.title("🤖 GitHin Master")
    st.markdown("---")
    st.caption("**TRẠNG THÁI HỆ THỐNG:**")
    st.success("✅ Đã kết nối OpenAI API thành công")
    
    st.markdown("---")
    if st.button("🧹 Dọn dẹp hội thoại"):
        st.session_state.messages = []
        st.rerun()
    
    st.markdown(f"<br><br><small style='color:#666;'>Phiên bản: v2.5 (Real API)</small>", unsafe_allow_html=True)

# --- KHỞI TẠO LỊCH SỬ CHAT ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Xin chào! Tôi là GitHin Master được hỗ trợ bởi OpenAI. Tôi sẵn sàng giúp bạn giải toán, viết code hoặc trả lời mọi câu hỏi."}
    ]

if len(st.session_state.messages) <= 1:
    st.title("GitHin Master AI")
    st.subheader("Hệ thống trợ lý thông minh đã sẵn sàng hoạt động.")

# Hiển thị lịch sử trò chuyện
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🧠"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# --- XỬ LÝ KHI NGƯỜI DÙNG NHẬP TIN NHẮN ---
if prompt := st.chat_input("Nhập câu hỏi hoặc yêu cầu của bạn..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🧠"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Đang suy nghĩ...")
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": m["role"], "content": m["content"]} 
                    for m in st.session_state.messages
                ],
                stream=True
            )
            
            full_response = ""
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")
            
            message_placeholder.markdown(full_response)
            
        except Exception as e:
            full_response = f"Đã xảy ra lỗi khi kết nối với OpenAI API: `{str(e)}`"
            message_placeholder.markdown(full_response)

    st.session_state.messages.append({"role": "assistant", "content": full_response})
