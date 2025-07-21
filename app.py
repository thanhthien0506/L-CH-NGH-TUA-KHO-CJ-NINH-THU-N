
import pandas as pd
import streamlit as st
import base64

# ========== CẤU HÌNH NGƯỜI DÙNG ==========
ACCOUNTS = {
    "CJNINHTHUAN": "NT2025",
    "ADMIN": "admin123"
}

def login():
    with st.sidebar:
        st.markdown("### 🔐 Đăng nhập hệ thống")
        username = st.text_input("Tên người dùng")
        password = st.text_input("Mật khẩu", type="password")
        if st.button("Đăng nhập"):
            if username in ACCOUNTS and ACCOUNTS[username] == password:
                st.session_state["login_success"] = True
                st.session_state["username"] = username
            else:
                st.error("Sai tài khoản hoặc mật khẩu")

def logout():
    if "login_success" in st.session_state:
        del st.session_state["login_success"]
    if "username" in st.session_state:
        del st.session_state["username"]
    st.rerun()

if "login_success" not in st.session_state:
    st.session_state["login_success"] = False

if not st.session_state["login_success"]:
    login()
    st.stop()

# ========== THÊM HÌNH NỀN ==========
def set_bg():
    with open("background.png", "rb") as img_file:
        b64_img = base64.b64encode(img_file.read()).decode()
    css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/png;base64,{b64_img}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: top center;
        background-attachment: fixed;
        color: white;
        background-color: #0e1a2b;
    }}
    .block-container {{
        padding-top: 2rem;
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

set_bg()

# ========== LOAD DỮ LIỆU ==========
@st.cache_data
def load_data():
    file_path = "lich_nghi_tua.xlsx"
    df_dl = pd.read_excel(file_path, sheet_name='DL')
    return df_dl

# ========== TRA CỨU ==========
def tra_cuu_theo_ten(df, ten):
    ten = ten.strip().lower()
    df['TEN_XU_LY'] = df['HỌ VÀ TÊN'].astype(str).str.strip().str.lower()
    row = df[df['TEN_XU_LY'] == ten]

    if row.empty:
        return 0, []

    ngay_cols = df.columns[4:-1] if 'TEN_XU_LY' in df.columns else df.columns[4:]
    row_data = row[ngay_cols].iloc[0]

    cac_ngay_nt = []
    for col in ngay_cols:
        if row_data[col] == 'NT':
            if isinstance(col, pd.Timestamp):
                cac_ngay_nt.append(col)
            else:
                try:
                    cac_ngay_nt.append(pd.to_datetime(col))
                except:
                    pass
    cac_ngay_nt = sorted(cac_ngay_nt)
    cac_ngay_nt = [d.strftime('%d/%m/%Y') for d in cac_ngay_nt]

    return len(cac_ngay_nt), cac_ngay_nt

def tra_cuu_theo_ngay(df, ngay_chon):
    try:
        ngay_chon = pd.to_datetime(ngay_chon, dayfirst=True)
    except:
        return None, None

    if ngay_chon not in df.columns:
        return [], []

    sale_list = df[df[ngay_chon] == 'NT']
    sale_names = sale_list[sale_list['VỊ TRÍ'].str.contains('SALE', na=False)]['HỌ VÀ TÊN'].tolist()
    cn_names = sale_list[~sale_list['VỊ TRÍ'].str.contains('SALE', na=False)]['HỌ VÀ TÊN'].tolist()

    return sale_names, cn_names

# ========== GIAO DIỆN ==========
st.set_page_config(page_title="CJ - Kho Trung Chuyển Ninh Thuận", layout="centered")
st.markdown("<h1 style='text-align: center; color: white;'>📋 TRA CỨU LỊCH LÀM VIỆC</h1>", unsafe_allow_html=True)

st.sidebar.markdown(f"👤 Đăng nhập: `{st.session_state['username']}`")
if st.sidebar.button("🚪 Đăng xuất"):
    logout()

df = load_data()
col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔍 Theo tên nhân viên:")
    ten = st.text_input("Tên người dùng:")
    if ten:
        so_ngay, ds_ngay = tra_cuu_theo_ten(df, ten)
        if so_ngay == 0:
            st.warning("Không có ngày nghỉ.")
        else:
            st.success(f"📅 Tổng số ngày nghỉ: {so_ngay}")
            for d in ds_ngay:
                st.markdown(f"- {d}")

with col2:
    st.markdown("### 🔍 Theo ngày làm việc:")
    ngay_input = st.text_input("Nhập ngày (vd: 22/07/2025):")
    if ngay_input:
        sales, workers = tra_cuu_theo_ngay(df, ngay_input)
        if sales is None:
            st.warning("Định dạng sai hoặc không có dữ liệu.")
        else:
            tong = len(sales) + len(workers)
            st.success(f"👥 Tổng số người nghỉ: {tong}")
            st.markdown("#### 🧾 SALE nghỉ:")
            for name in sales:
                st.markdown(f"- {name}")
            st.markdown("#### 🧾 CÔNG NHÂN nghỉ:")
            for name in workers:
                st.markdown(f"- {name}")
