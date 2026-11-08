import streamlit as st
import pandas as pd
import time

# 1. GIẢI LẬP DATABASE (MASTER DATA) TỪ HÃNG TÀU (Truyền qua EDI)
# Trong thực tế, dữ liệu này nằm ở server hãng tàu, E-port sẽ gọi API để lấy về
master_data = pd.DataFrame({
    "So_Container": ["ZIMU1234567", "MSCU9876543", "CMAU1122334"],
    "Hang_Tau": ["ZIM", "MSC", "CMA CGM"],
    "Nhiet_Do_Chuan": [-18.0, 5.0, -20.0],  # Độ C
    "Thong_Gio_Chuan": [0, 15, 0]           # cbm/h
})

def main():
    st.set_page_config(page_title="E-port Sandbox - TCHP", layout="centered")
    
    st.image("https://saigonnewport.com.vn/images/logo.png", width=150) # Logo giả lập
    st.title("Mô phỏng E-port: Đăng ký Hạ bãi Container Lạnh")
    st.write("---")

    # 2. GIAO DIỆN FRONT-END (Khách hàng nhập liệu - Giữ nguyên không đổi)
    st.subheader("Nhập thông tin khai báo (Khách hàng)")
    col1, col2 = st.columns(2)
    
    with col1:
        hang_tau = st.selectbox("Chọn Hãng Tàu", ["ZIM", "MSC", "CMA CGM", "Khác"])
        so_cont = st.text_input("Số Container (VD: ZIMU1234567)")
    
    with col2:
        nhiet_do_khai_bao = st.number_input("Nhiệt độ cài đặt (°C)", value=0.0, step=0.1)
        thong_gio_khai_bao = st.number_input("Thông gió (cbm/h)", value=0, step=1)

    # 3. NÚT XỬ LÝ (Kích hoạt Module chạy ngầm)
    if st.button("Thanh toán & Đăng ký Gate-in", type="primary"):
        if not so_cont:
            st.warning("Vui lòng nhập số container!")
            return

        with st.spinner("Đang kết nối EDI đối chiếu Master Data của hãng tàu..."):
            time.sleep(1.5) # Giả lập độ trễ khi gọi API
            
            # Module Middleware đối chiếu dữ liệu ngầm
            cont_data = master_data[master_data["So_Container"] == so_cont.upper()]
            
            if cont_data.empty:
                st.info("⚠️ Không tìm thấy dữ liệu Booking từ hãng tàu cho Container này. Chuyển sang luồng xử lý thủ công.")
            else:
                nhiet_chuan = float(cont_data["Nhiet_Do_Chuan"].iloc[0])
                gio_chuan = int(cont_data["Thong_Gio_Chuan"].iloc[0])
                
                # Logic kiểm tra điểm nghẽn
                if (nhiet_do_khai_bao == nhiet_chuan) and (thong_gio_khai_bao == gio_chuan):
                    st.success("✅ THÀNH CÔNG! Thông số khớp với Booking.")
                    st.write("**Mã Code Gate-in:** TCHP-883921")
                    st.write("*Hệ thống tự động cấp phiếu giao nhận (EIR).*")
                else:
                    st.error("🚨 TỪ CHỐI CẤP PHIẾU GIAO NHẬN (LỖI NGOẠI LỆ)")
                    st.write(f"**Lý do:** Thông số khai báo KHÔNG KHỚP với dữ liệu gốc của hãng tàu {hang_tau}.")
                    st.write(f"- Nhiệt độ chuẩn: {nhiet_chuan}°C (Khai báo: {nhiet_do_khai_bao}°C)")
                    st.write(f"- Thông gió chuẩn: {gio_chuan} cbm/h (Khai báo: {thong_gio_khai_bao} cbm/h)")
                    st.warning("👉 Vui lòng di chuyển đến quầy ĐỘI THƯƠNG VỤ để kiểm tra lại chứng từ và xử lý ngoại lệ.")

if __name__ == "__main__":
    main()