import streamlit as st
import pandas as pd
import numpy as np
import io

# Cấu hình trang hiển thị của Streamlit
st.set_page_config(
    page_title="Hệ thống Phân tích Dữ liệu Xổ số",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("📊 Hệ thống Phân tích Dữ liệu Xổ số (Nghiên cứu Toán học)")
st.caption("Ứng dụng chạy thử nghiệm trên nền tảng Streamlit Cloud - Đầy đủ tính năng thống kê toán học")

# 1. Tạo dữ liệu mẫu nếu người dùng chưa upload file
def generate_sample_data():
    dates = pd.date_range(start="2025-01-01", periods=100, freq="D")
    data = []
    for i, date in enumerate(dates):
        # Mô phỏng chọn 6 số ngẫu nhiên từ 1 đến 55 không trùng nhau
        nums = sorted(np.random.choice(range(1, 56), 6, replace=False).tolist())
        data.append({
            "Kỳ quay": f"{i+1:05d}",
            "Ngày quay": date.strftime("%Y-%m-%d"),
            "Số 1": nums[0], "Số 2": nums[1], "Số 3": nums[2],
            "Số 4": nums[3], "Số 5": nums[4], "Số 6": nums[5]
        })
    return pd.DataFrame(data)

# 2. Thanh Menu bên trái (Sidebar)
st.sidebar.header("📁 Quản lý Dữ liệu")
uploaded_file = st.sidebar.file_saver = st.sidebar.file_uploader("Upload dữ liệu (CSV/Excel)", type=["csv", "xlsx"])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        st.sidebar.success("Tải dữ liệu của bạn thành công!")
    except Exception as e:
        st.sidebar.error(f"Lỗi đọc file: {e}")
        df = generate_sample_data()
else:
    st.sidebar.info("Đang sử dụng dữ liệu mô phỏng 100 kỳ gần nhất.")
    df = generate_sample_data()

# Lọc chu kỳ quay số
st.sidebar.header("⚙️ Bộ lọc Chu kỳ")
period = st.sidebar.selectbox("Chọn số kỳ phân tích gần nhất:", [10, 30, 50, 100, "Toàn bộ"])

if period != "Toàn bộ":
    df_analysis = df.tail(int(period)).copy()
else:
    df_analysis = df.copy()

# Tách ma trận số trúng thưởng để tính toán chuyên sâu
num_cols = ["Số 1", "Số 2", "Số 3", "Số 4", "Số 5", "Số 6"]
matrix_nums = df_analysis[num_cols].values
all_numbers = matrix_nums.flatten()

# --- GIAO DIỆN TỔNG QUAN (DASHBOARD) ---
st.header("📈 Dashboard Tổng quan")
col1, col2, col3 = st.columns(3)
col1.metric("Tổng số kỳ phân tích", len(df_analysis))
col2.metric("Số nhỏ nhất xuất hiện", int(all_numbers.min()))
col3.metric("Số lớn nhất xuất hiện", int(all_numbers.max()))

# 3. Module Thống kê tần suất (Frequency Analysis)
st.subheader("🔢 Thống kê tần suất xuất hiện (Ma trận 1-55)")
freq_series = pd.Series(all_numbers).value_counts().reindex(range(1, 56), fill_value=0)
df_freq = pd.DataFrame({"Số": freq_series.index, "Số lần về": freq_series.values})
df_freq["Tỷ lệ %"] = ((df_freq["Số lần về"] / len(df_analysis)) * 100).round(2)

# Hiển thị biểu đồ tần suất trực quan
st.bar_chart(df_freq.set_index("Số")["Số lần về"])

# 4. Phân tích Chẵn Lẻ & Lớn Nhỏ
st.subheader("⚖️ Phân tích xu hướng hình học (Chẵn/Lẻ - Lớn/Nhỏ)")
c_le, c_chan = st.columns(2)

even_count = np.sum(all_numbers % 2 == 0)
odd_count = len(all_numbers) - even_count

small_count = np.sum(all_numbers <= 27)
big_count = len(all_numbers) > 27

with c_le:
    st.write("**Tỷ lệ Chẵn / Lẻ:**")
    st.write(f"🔹 Số chẵn: {even_count} lần ({even_count/len(all_numbers)*100:.1f}%)")
    st.write(f"🔹 Số lẻ: {odd_count} lần ({odd_count/len(all_numbers)*100:.1f}%)")

with c_chan:
    st.write("**Tỷ lệ Lớn (28-55) / Nhỏ (1-27):**")
    st.write(f"🔹 Nhỏ (1-27): {small_count} lần ({small_count/len(all_numbers)*100:.1f}%)")
    st.write(f"🔹 Lớn (28-55): {np.sum(all_numbers >= 28)} lần ({np.sum(all_numbers >= 28)/len(all_numbers)*100:.1f}%)")

# 5. Phân tích Khoảng cách (Gap Analysis)
st.subheader("⏳ Phân tích khoảng cách (Số kỳ chưa về gần nhất)")
gaps = {}
for n in range(1, 56):
    found_indices = np.where(matrix_nums == n)[0]
    if len(found_indices) > 0:
        # Số kỳ kể từ lần cuối xuất hiện đến kỳ gần nhất
        last_seen_index = found_indices[-1]
        gaps[n] = len(matrix_nums) - 1 - last_seen_index
    else:
        gaps[n] = len(matrix_nums) # Chưa về bao giờ trong chu kỳ

df_gap = pd.DataFrame(list(gaps.items()), columns=["Số", "Số kỳ vắng mặt"]).set_index("Số")
st.line_chart(df_gap)

# 6. Xem trước và xuất báo cáo dữ liệu sạch
st.subheader("📋 Xem danh sách dữ liệu gốc")
st.dataframe(df_analysis, use_container_width=True)

# Nút tải báo cáo Excel
towrite = io.BytesIO()
df_analysis.to_excel(towrite, index=False, header=True)
towrite.seek(0)
st.download_button(label="📥 Xuất báo cáo Excel", data=towrite, file_name="bao_cao_lo_trinh.xlsx", mime="application/vnd.ms-excel")