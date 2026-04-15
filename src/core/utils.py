import pygame

def load_spritesheet(filename, rows, cols):
    # Load ảnh và hỗ trợ độ trong suốt
    sheet = pygame.image.load(filename).convert_alpha()
    
    # Tính toán kích thước mỗi ô (frame)
    frame_width = sheet.get_width() // cols
    frame_height = sheet.get_height() // rows
    
    sprites = []
    for r in range(rows):
        row_frames = []
        for c in range(cols):
            # Xác định vùng cắt
            rect = pygame.Rect(c * frame_width, r * frame_height, frame_width, frame_height)
            # Cắt ảnh con từ ảnh gốc
            frame = sheet.subsurface(rect)
        sprites.append(row_frames)
    return sprites

def load_spritesheet_auto(filename, scale=2, frame_config=None):
    import os, re
    sheet = pygame.image.load(filename).convert_alpha()
    w, h = sheet.get_size()
    
    # Tính số frames hoặc frame_width
    frame_width = None
    
    # 1. Thử đọc từ config hardcode (chỉ dùng cho các frame dị dạng)
    base = os.path.basename(filename)
    if frame_config and base in frame_config:
        frames = frame_config[base]
        frame_width = w // frames
    
    # 2. Thử đọc từ số đuôi _stripXX trong tên file
    if not frame_width:
        match = re.search(r'_strip(\d+)', base)
        if match:
            frames = int(match.group(1))
            frame_width = w // frames
            
    # 3. Mặc định Fallback (Đoán bằng width chia đều nhưng phải hợp lý)
    if not frame_width:
        # Nếu chiều dọc chia hết
        if w % h == 0:
            frame_width = h
        else:
            # Thuật toán cạn kiệt tìm cái gần với hình vuông nhất
            cands = [i for i in range(50, int(w)) if w % i == 0]
            if cands:
                frame_width = min(cands, key=lambda x: abs(x - h))
            else:
                frame_width = w # Khỏi chia

    sprites = []
    print(f"Loading {base} with width={w}, h={h}, frame_width={frame_width}")
    for i in range(w // frame_width):
        rect = pygame.Rect(i * frame_width, 0, frame_width, h)
        frame = sheet.subsurface(rect)
        if scale != 1:
            frame = pygame.transform.scale(frame, (int(frame_width * scale), int(h * scale)))
        sprites.append(frame)
    return sprites

def load_individual_sprites(folder_path, prefix, scale=2):
    import os
    sprites = []
    if not os.path.exists(folder_path):
        return sprites
        
    # Lấy tất cả ảnh khớp prefix (ví dụ: 'adventurer-run') và sắp xếp theo số
    valid_files = [f for f in os.listdir(folder_path) if f.startswith(prefix) and f.endswith('.png')]
    valid_files.sort()
    
    for f in valid_files:
        path = os.path.join(folder_path, f)
        frame = pygame.image.load(path).convert_alpha()
        if scale != 1:
            w, h = frame.get_size()
            frame = pygame.transform.scale(frame, (int(w * scale), int(h * scale)))
        sprites.append(frame)
    return sprites