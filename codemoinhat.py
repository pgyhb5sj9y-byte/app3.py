import streamlit as st
import pandas as pd
import datetime

# --- CẤU HÌNH DATABASE GIẢ LẬP ---
if "master_data" not in st.session_state:
    # Dữ liệu mặc định ban đầu
    st.session_state.master_data = pd.DataFrame({
        "So_Container": ["ZIMU1234567", "MSCU9876543"],
        "Hang_Tau": ["ZIM", "MSC"],
        "Nhiet_Do_Chuan": [-18.0, 5.0],
        "Thong_Gio_Chuan": [0, 15]
    })

if "topovn_db" not in st.session_state:
    st.session_state.topovn_db = pd.DataFrame(columns=["Thoi_Gian", "So_Container", "Nhiet_Do_Thuc_Te", "Trang_Thai"])

# --- GIAO DIỆN CHÍNH ---
st.set_page_config(page_title="TCHP Sandbox", layout="centered")
st.sidebar.title("Hệ Sinh Thái TCHP")
menu = st.sidebar.radio("Chọn phân hệ chức năng:", 
                        ["1. Nạp Master Data (Kế hoạch/Hãng tàu)", 
                         "2. Cổng E-port (Khách hàng)", 
                         "3. Mobile App (Bãi Lạnh)"])

# ==========================================
# PHÂN HỆ 1: NẠP DỮ LIỆU GỐC (MASTER DATA)
# ==========================================
if menu == "1. Nạp Master Data (Kế hoạch/Hãng tàu)":
    st.header("🗄️ Cổng Upload Master Data (Hãng tàu)")
    st.write("Khu vực dành cho Hãng tàu truyền EDI hoặc nhân viên Cảng upload file Excel Booking.")
    
    # Hiển thị database hiện tại
    st.dataframe(st.session_state.master_data, use_container_width=True)
    
    st.subheader("Thêm dữ liệu thủ công (Giả lập Upload)")
    col1, col2, col3, col4 = st.columns(4)
    with col1: new_cont = st.text_input("Số Cont")
    with col2: new_hang = st.text_input("Hãng Tàu")
    with col3: new_nhiet = st.number_input("Nhiệt chuẩn", value=0.0)
    with col4: new_gio = st.number_input("Gió chuẩn", value=0)
    
    if st.button("Lưu vào Hệ thống (TOPS)"):
        if new_cont:
            new_row = pd.DataFrame([{"So_Container": new_cont.upper(), "Hang_Tau": new_hang, "Nhiet_Do_Chuan": new_nhiet, "Thong_Gio_Chuan": new_gio}])
            st.session_state.master_data = pd.concat([st.session_state.master_data, new_row], ignore_index=True)
            st.success(f"Đã nạp Master Data cho container {new_cont.upper()}")
            st.rerun()

# ==========================================
# PHÂN HỆ 2: CỔNG E-PORT (CỦA KIỆT)
# ==========================================
elif menu == "2. Cổng E-port (Khách hàng)":
    st.header("💻 Cổng E-port: Đăng ký Gate-in")
    st.info("Module chạy ngầm sẽ lấy Master Data từ phân hệ 1 để đối chiếu.")
    
    col1, col2 = st.columns(2)
    with col1:
        so_cont_khai = st.text_input("Số Container (VD: ZIMU1234567)")
    with col2:
        nhiet_khai = st.number_input("Nhiệt độ khai báo (°C)", value=0.0, step=0.1)
        gio_khai = st.number_input("Thông gió (cbm/h)", value=0)

    if st.button("Thanh toán & Đăng ký", type="primary"):
        if so_cont_khai:
            cont_data = st.session_state.master_data[st.session_state.master_data["So_Container"] == so_cont_khai.upper()]
            if cont_data.empty:
                st.error("Chưa có Booking từ hãng tàu. Vui lòng liên hệ Đội Thương Vụ.")
            else:
                nhiet_chuan = float(cont_data["Nhiet_Do_Chuan"].iloc[0])
                gio_chuan = int(cont_data["Thong_Gio_Chuan"].iloc[0])
                
                if (nhiet_khai == nhiet_chuan) and (gio_khai == gio_chuan):
                    st.success("✅ THÀNH CÔNG! Đã cấp mã Gate-in.")
                else:
                    st.error("🚨 TỪ CHỐI CẤP PHIẾU. Sai thông số với Hãng tàu.")
                    st.write(f"Dữ liệu gốc: {nhiet_chuan}°C | Khai báo: {nhiet_khai}°C")

# ==========================================
# PHÂN HỆ 3: MOBILE APP TẠI BÃI LẠNH (CỦA LINH/KIỆT)
# ==========================================
elif menu == "3. Mobile App (Bãi Lạnh)":
    st.header("📱 App Nhân viên Kỹ thuật Lạnh")
    st.write("Nhân viên quét mã vạch hoặc nhập số container để đọc dữ liệu hệ thống.")
    
    cont_scan = st.text_input("🔍 Nhập/Quét số Container hạ bãi:")
    
    if cont_scan:
        cont_data = st.session_state.master_data[st.session_state.master_data["So_Container"] == cont_scan.upper()]
        
        if cont_data.empty:
            st.warning("Không tìm thấy container này trong hệ thống.")
        else:
            nhiet_chuan = float(cont_data["Nhiet_Do_Chuan"].iloc[0])
            st.info(f"**Thông số Booking (Master Data):** Yêu cầu cài đặt **{nhiet_chuan} °C**")
            
            st.write("---")
            nhiet_thuc_te = st.number_input("🌡️ Nhập nhiệt độ hiển thị trên màn hình máy lạnh:", value=0.0)
            tinh_trang = st.selectbox("Tình trạng máy lạnh:", ["Bình thường", "Báo lỗi / Hư hỏng"])
            
            if st.button("Lưu lên TOPOVN"):
                # Ghi nhận vào DB
                now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log = pd.DataFrame([{"Thoi_Gian": now, "So_Container": cont_scan.upper(), "Nhiet_Do_Thuc_Te": nhiet_thuc_te, "Trang_Thai": tinh_trang}])
                st.session_state.topovn_db = pd.concat([st.session_state.topovn_db, log], ignore_index=True)
                
                # Cảnh báo nếu nhiệt độ máy chưa về đúng chuẩn
                if (nhiet_thuc_te > nhiet_chuan + 3) or (nhiet_thuc_te < nhiet_chuan - 3):
                    st.warning("⚠️ Đã lưu hệ thống. LƯU Ý: Nhiệt độ thực tế đang chênh lệch quá 3 độ so với Booking. Đang theo dõi tiến trình làm lạnh.")
                elif tinh_trang != "Bình thường":
                    st.error("🚨 Đã lưu sự cố. Đang phát tín hiệu báo cho ĐĐHT và Hãng tàu.")
                else:
                    st.success("✅ Đã lưu TOPOVN. Thông số an toàn. Cho phép cắm điện.")
                    
    st.write("---")
    st.subheader("Dữ liệu đã đẩy lên TOPOVN")
    st.dataframe(st.session_state.topovn_db, use_container_width=True)
