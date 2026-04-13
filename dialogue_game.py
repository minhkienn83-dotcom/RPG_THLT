import os
import time
import sys

# --- BƯỚC 1: ĐỊNH NGHĨA Ô-TÔ-MÁT (FA) BẰNG DICTIONARY ---
# Ở đây FA được định nghĩa bởi:
# Q: Tập các trạng thái (TRUNG_LAP, TO_MO, NGHI_NGO, THAN_THIEN, TUC_GIAN, CHO_PHEP_QUA, TRUC_XUAT)
# Σ (Sigma): Tập các lựa chọn của người chơi ('1', '2', '3')
# q0: Trạng thái bắt đầu ('TRUNG_LAP')
# F: Tập trạng thái kết thúc ('CHO_PHEP_QUA', 'TRUC_XUAT')
# δ (Delta): Hàm chuyển trạng thái được tích hợp trong 'options' của mỗi từ điển

dialogue_automaton = {
    'TRUNG_LAP': {
        'mo_ta': 'Một giọng nói cổ xưa vang lên từ hư không: "Kẻ phàm trần... Ngươi làm gì ở nơi linh thiêng này?"',
        'options': {
            '1': ("Kính chào ngài, tôi là một nhà thám hiểm vô tình lạc đến đây.", 'TO_MO'),
            '2': ("Ta không có nghĩa vụ phải trả lời ngươi!", 'TUC_GIAN'),
            '3': ("Tôi đến để tìm kho báu của ngôi đền.", 'NGHI_NGO')
        },
        'is_final': False
    },
    'TO_MO': {
        'mo_ta': 'Linh hồn có vẻ tò mò: "Một nhà thám hiểm sao... Ngươi tìm kiếm điều gì ở vùng đất bị lãng quên này?"',
        'options': {
            '1': ("Tôi tìm kiếm tri thức, muốn tìm hiểu về lịch sử vĩ đại của nơi này.", 'THAN_THIEN'),
            '2': ("Tôi nghe nói ở đây có vũ khí huyền thoại.", 'NGHI_NGO'),
        },
        'is_final': False
    },
    'NGHI_NGO': {
        'mo_ta': 'Giọng nói trở nên lạnh lùng: "Ngươi cũng như bao kẻ tham lam khác. Nơi này không chào đón ngươi. Hãy rời đi!"',
        'options': {
            '1': ("Xin ngài bình tĩnh, tôi không có ác ý. Xin hãy cho tôi một cơ hội.", 'TO_MO'),
            '2': ("Nếu không cho thì ta sẽ tự mình lấy!", 'TUC_GIAN'),
        },
        'is_final': False
    },
    'THAN_THIEN': {
        'mo_ta': 'Linh hồn dường như mỉm cười: "Hiếm có kẻ nào đến đây vì tri thức. Ta có thiện cảm với ngươi. Hãy nói, ngươi muốn gì?"',
        'options': {
            '1': ("Xin ngài hãy cho phép tôi được đi qua cánh cổng này để tiếp tục hành trình.", 'CHO_PHEP_QUA'),
            '2': ("Hãy cho tôi sức mạnh của ngài!", 'NGHI_NGO'),
        },
        'is_final': False
    },
    'TUC_GIAN': {
        'mo_ta': 'Không gian rung chuyển. Giọng nói gầm lên: "SỰ NGÔNG CUỒNG CỦA NGƯƠI SẼ PHẢI TRẢ GIÁ!!!"',
        'options': {
            # Từ trạng thái này, mọi lựa chọn đều dẫn đến kết cục xấu
            '1': ("(Cố gắng bỏ chạy)", 'TRUC_XUAT'),
            '2': ("(Rút vũ khí)", 'TRUC_XUAT'),
        },
        'is_final': False
    },
    # --- CÁC TRẠNG THÁI KẾT THÚC ---
    'CHO_PHEP_QUA': {
        'mo_ta': 'Linh hồn nói: "Được thôi, người tìm kiếm tri thức. Con đường ở phía trước. Hãy đi đi."\n\n[=== BẠN ĐÃ THUYẾT PHỤC THÀNH CÔNG! (THIÊN ĐƯỜNG MỞ RA) ===]',
        'is_final': True
    },
    'TRUC_XUAT': {
        'mo_ta': 'Một luồng năng lượng vô hình hất văng bạn ra khỏi ngôi đền. Cánh cổng đóng sập lại mãi mãi.\n\n[=== BẠN ĐÃ THẤT BẠI! (GAME OVER) ===]',
        'is_final': True
    }
}

# --- CÁC HÀM TIỆN ÍCH HIỂU ỨNG ---

def clear_screen():
    """Hàm xóa màn hình cho gọn gàng."""
    os.system('cls' if os.name == 'nt' else 'clear')

def type_text(text, delay=0.03):
    """Hiệu ứng gõ chữ từng ký tự cho giống RPG."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

# --- BƯỚC 2: VIẾT VÒNG LẶP CHÍNH CỦA TRÒ CHƠI ---

def run_game():
    current_state_key = 'TRUNG_LAP' # Trạng thái bắt đầu q₀

    clear_screen()
    print("==================================================")
    print("      CHÀO MỪNG ĐẾN VỚI NGÔI ĐỀN BỊ LÃNG QUÊN      ")
    print("           (Trò chơi dựa trên Ô-tô-mát)           ")
    print("==================================================")
    time.sleep(2)

    while True:
        clear_screen()
        current_state_data = dialogue_automaton[current_state_key]

        # In ra lời thoại của NPC
        print("\n" + "="*50)
        print("                 LINH HỒN CỔ ĐẠI                  ")
        print("="*50 + "\n")
        
        # Thêm hiệu ứng gõ chữ cho lời nói
        type_text(current_state_data['mo_ta'], delay=0.02)
        print("\n" + "-"*50)

        # Nếu là trạng thái kết thúc (Final State), dừng trò chơi
        if current_state_data['is_final']:
            break

        # In ra các lựa chọn cho người chơi (Các transition)
        print("\nLựa chọn của bạn:")
        for key, (text, next_state) in current_state_data['options'].items():
            print(f"  [{key}] - {text}")

        # Lấy lựa chọn từ người chơi (Ký hiệu đầu vào input symbol)
        choice = input("\n> Quyết định của bạn (Nhập 1, 2, ...): ").strip()

        # Hàm chuyển δ(q, a) = p
        if choice in current_state_data['options']:
            # Lấy ra tên của trạng thái tiếp theo p
            next_state_key = current_state_data['options'][choice][1]
            current_state_key = next_state_key # Cập nhật trạng thái hiện tại
        else:
            print("\n[!] Lựa chọn không hợp lệ hoặc bạn im lặng quá lâu. Vui lòng nhập lại...")
            time.sleep(2) # Dừng 2 giây để người chơi đọc lại

# --- BƯỚC 3: KHỞI ĐỘNG TRÒ CHƠI ---
if __name__ == "__main__":
    try:
        run_game()
    except KeyboardInterrupt:
        print("\n\nBạn đã rời khỏi ngôi đền giữa chừng...")
        sys.exit()
