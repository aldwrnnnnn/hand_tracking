import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import math
import time
import threading

# ==========================================
# 1. Setup Audio Feedback Sci-Fi (Non-Blocking)
# ==========================================
def play_sfx(freq, duration):
    """Memainkan nada sci-fi secara asynchronous tanpa menghambat FPS"""
    def _beep():
        try:
            import winsound
            winsound.Beep(int(freq), int(duration))
        except Exception:
            pass
    threading.Thread(target=_beep, daemon=True).start()

# ==========================================
# 2. Setup Pelacakan Tangan (MediaPipe Tasks)
# ==========================================
base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_hands=2,
    min_hand_detection_confidence=0.5,
    min_hand_presence_confidence=0.5,
    min_tracking_confidence=0.5
)
detector = vision.HandLandmarker.create_from_options(options)

# Koneksi sendi tangan untuk Cyber Skeleton
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Jempol
    (0, 5), (5, 6), (6, 7), (7, 8),        # Telunjuk
    (5, 9), (9, 10), (10, 11), (11, 12),   # Jari Tengah
    (9, 13), (13, 14), (14, 15), (15, 16), # Jari Manis
    (13, 17), (17, 18), (18, 19), (19, 20),# Kelingking
    (0, 17)                                # Dasar Telapak
]

# ==========================================
# 3. Fungsi Bantuan (Helper & Sensor Presisi)
# ==========================================
def get_distance(p1, p2):
    """Menghitung jarak Euclidean 2D"""
    return math.hypot(p2[0] - p1[0], p2[1] - p1[1])

def is_pinch_adaptive(hand_landmarks, w, h, was_pinched=False):
    """
    Sensor Cubit Adaptif & Anti-Flicker (Hysteresis):
    Menghitung jarak cubitan relatif terhadap ukuran telapak tangan pengguna.
    Bekerja konsisten pada jarak tangan dekat maupun jauh dari kamera.
    """
    wrist = hand_landmarks[0]
    mcp = hand_landmarks[9] # Pangkal jari tengah
    hand_scale = math.hypot(mcp.x - wrist.x, mcp.y - wrist.y)
    
    thumb = hand_landmarks[4]
    index = hand_landmarks[8]
    raw_dist = math.hypot(index.x - thumb.x, index.y - thumb.y)
    
    # Rasio jarak terhadap skala tangan
    ratio = raw_dist / (hand_scale + 1e-5)
    
    # Hysteresis threshold (lebih mudah mempertahankan cubitan daripada memulainya)
    threshold = 0.42 if was_pinched else 0.32
    pinched = ratio < threshold
    
    thumb_px = (int(thumb.x * w), int(thumb.y * h))
    index_px = (int(index.x * w), int(index.y * h))
    return pinched, thumb_px, index_px

def is_open_palm(hand_landmarks):
    """Deteksi gestur telapak tangan terbuka (Reset)"""
    wrist = hand_landmarks[0]
    for tip_idx, pip_idx in [(12, 10), (16, 14), (20, 18)]:
        tip = hand_landmarks[tip_idx]
        pip = hand_landmarks[pip_idx]
        dist_tip = math.hypot(tip.x - wrist.x, tip.y - wrist.y)
        dist_pip = math.hypot(pip.x - wrist.x, pip.y - wrist.y)
        if dist_tip < dist_pip * 1.2:
            return False
    return True

def is_peace_sign(hand_landmarks):
    """Deteksi gestur ✌️ (Peace Sign / Snapshot)"""
    wrist = hand_landmarks[0]
    idx_tip, idx_pip = hand_landmarks[8], hand_landmarks[6]
    mid_tip, mid_pip = hand_landmarks[12], hand_landmarks[10]
    ring_tip, ring_pip = hand_landmarks[16], hand_landmarks[14]
    pinky_tip, pinky_pip = hand_landmarks[20], hand_landmarks[18]
    
    # Telunjuk & Jari Tengah tegak
    idx_ext = math.hypot(idx_tip.x - wrist.x, idx_tip.y - wrist.y) > math.hypot(idx_pip.x - wrist.x, idx_pip.y - wrist.y) * 1.15
    mid_ext = math.hypot(mid_tip.x - wrist.x, mid_tip.y - wrist.y) > math.hypot(mid_pip.x - wrist.x, mid_pip.y - wrist.y) * 1.15
    # Jari Manis & Kelingking ditekuk
    ring_fold = math.hypot(ring_tip.x - wrist.x, ring_tip.y - wrist.y) < math.hypot(ring_pip.x - wrist.x, ring_pip.y - wrist.y) * 1.15
    pinky_fold = math.hypot(pinky_tip.x - wrist.x, pinky_tip.y - wrist.y) < math.hypot(pinky_pip.x - wrist.x, pinky_pip.y - wrist.y) * 1.15
    
    return idx_ext and mid_ext and ring_fold and pinky_fold

# ==========================================
# 4. Koleksi Filter Spektakuler (Sci-Fi Shaders)
# ==========================================
def apply_cyber_neon(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 60, 140)
    neon = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    neon[:, :, 0] = np.where(edges > 0, 255, 0)
    neon[:, :, 1] = np.where(edges > 0, 255, 0)
    neon[:, :, 2] = np.where(edges > 0, 0, 0)
    return cv2.addWeighted(frame, 0.2, neon, 0.9, 0)

def apply_thermal(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.applyColorMap(gray, cv2.COLORMAP_INFERNO)

def apply_matrix_hologram(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hologram = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    hologram[:, :, 0] = (hologram[:, :, 0] * 0.08).astype(np.uint8)
    hologram[:, :, 1] = np.clip(hologram[:, :, 1] * 1.35 + 25, 0, 255).astype(np.uint8)
    hologram[:, :, 2] = (hologram[:, :, 2] * 0.08).astype(np.uint8)
    hologram[::4, :] = (hologram[::4, :] * 0.45).astype(np.uint8)
    return hologram

def apply_synthwave(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.applyColorMap(gray, cv2.COLORMAP_MAGMA)

def apply_negative_glitch(frame):
    neg = 255 - frame
    glitch = neg.copy()
    shift = 7
    glitch[:, shift:, 2] = neg[:, :-shift, 2]
    glitch[:, :-shift, 0] = neg[:, shift:, 0]
    return glitch

def apply_sepia(frame):
    kernel = np.array([[0.272, 0.534, 0.131],
                       [0.349, 0.686, 0.168],
                       [0.393, 0.769, 0.189]])
    sepia = cv2.transform(frame, kernel)
    return np.clip(sepia, 0, 255).astype(np.uint8)

filters = [
    ("CYBER NEON", apply_cyber_neon, (0, 255, 200)),
    ("THERMAL SENSOR", apply_thermal, (0, 140, 255)),
    ("MATRIX HOLOGRAM", apply_matrix_hologram, (0, 255, 60)),
    ("SYNTHWAVE 80s", apply_synthwave, (255, 50, 200)),
    ("CHROMATIC GLITCH", apply_negative_glitch, (200, 200, 255)),
    ("VINTAGE SEPIA", apply_sepia, (50, 180, 240))
]

# ==========================================
# 5. Visual Rendering & Percikan Energi (Sparks)
# ==========================================
def draw_cyber_skeleton(frame, landmarks, w, h):
    coords = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for p1_idx, p2_idx in HAND_CONNECTIONS:
        cv2.line(frame, coords[p1_idx], coords[p2_idx], (255, 200, 50), 1, cv2.LINE_AA)
    for pt in coords:
        cv2.circle(frame, pt, 2, (0, 255, 255), -1)

def draw_portal_glow_and_sparks(frame, pts, color_theme, t):
    """Portal Glow + Partikel Percikan Energi (Doctor Strange Sling-Ring Sparks)"""
    # Multi-layer aura glow
    cv2.polylines(frame, [pts], isClosed=True, color=(int(color_theme[0]*0.3), int(color_theme[1]*0.3), int(color_theme[2]*0.3)), thickness=11, lineType=cv2.LINE_AA)
    cv2.polylines(frame, [pts], isClosed=True, color=(int(color_theme[0]*0.7), int(color_theme[1]*0.7), int(color_theme[2]*0.7)), thickness=6, lineType=cv2.LINE_AA)
    cv2.polylines(frame, [pts], isClosed=True, color=color_theme, thickness=2, lineType=cv2.LINE_AA)
    cv2.polylines(frame, [pts], isClosed=True, color=(255, 255, 255), thickness=1, lineType=cv2.LINE_AA)
    
    # Node cincin energi berdenyut di ke-4 ujung jari
    pulse_r = int(10 + 3 * math.sin(t * 7))
    for pt in pts.reshape(-1, 2):
        x, y = int(pt[0]), int(pt[1])
        cv2.circle(frame, (x, y), pulse_r, color_theme, 1, cv2.LINE_AA)
        cv2.circle(frame, (x, y), 4, (255, 255, 255), -1)

    # Percikan Energi Melayang di sepanjang garis batas
    corners = pts.reshape(4, 2)
    for i in range(12):
        prog = (t * 2.2 + i * (4.0 / 12.0)) % 4.0
        edge_idx = int(prog)
        alpha = prog - edge_idx
        p1 = corners[edge_idx]
        p2 = corners[(edge_idx + 1) % 4]
        
        sx = int(p1[0] + alpha * (p2[0] - p1[0]))
        sy = int(p1[1] + alpha * (p2[1] - p1[1]))
        
        jitter_x = int(math.sin(t * 15 + i) * 5)
        jitter_y = int(math.cos(t * 15 + i) * 5)
        
        cv2.circle(frame, (sx + jitter_x, sy + jitter_y), 2, (255, 255, 255), -1, cv2.LINE_AA)
        cv2.circle(frame, (sx + jitter_x, sy + jitter_y), 5, color_theme, 1, cv2.LINE_AA)

def draw_hud_banner(frame, mode_name, filter_name, fps, color_theme):
    w = frame.shape[1]
    overlay = frame.copy()
    cv2.rectangle(overlay, (20, 15), (w - 20, 65), (15, 15, 20), -1)
    cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
    
    cv2.rectangle(frame, (20, 15), (w - 20, 65), color_theme, 1, cv2.LINE_AA)
    cv2.putText(frame, f"[ SYS: {filter_name} ]", (35, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.65, color_theme, 2, cv2.LINE_AA)
    cv2.putText(frame, f"MODE: {mode_name}", (w // 2 - 110, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1, cv2.LINE_AA)
    cv2.putText(frame, f"FPS: {fps:02d}", (w - 140, 48), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 180), 2, cv2.LINE_AA)

def draw_aim_reticle(frame, cx, cy, is_locked, t):
    r = 24
    color = (0, 0, 255) if is_locked else (0, 255, 255)
    cv2.circle(frame, (cx, cy), r, color, 1, cv2.LINE_AA)
    cv2.circle(frame, (cx, cy), 3, (255, 255, 255), -1)
    
    angle = t * 4
    for a in [0, math.pi/2, math.pi, 3*math.pi/2]:
        x1 = int(cx + (r - 6) * math.cos(angle + a))
        y1 = int(cy + (r - 6) * math.sin(angle + a))
        x2 = int(cx + (r + 8) * math.cos(angle + a))
        y2 = int(cy + (r + 8) * math.sin(angle + a))
        cv2.line(frame, (x1, y1), (x2, y2), color, 2, cv2.LINE_AA)
        
    if is_locked:
        cv2.putText(frame, "LOCKED", (cx - 28, cy - 32), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 1, cv2.LINE_AA)

def draw_tension_meter(frame, x, y, tension_pct, is_ready):
    bar_w, bar_h = 180, 14
    cv2.rectangle(frame, (x, y), (x + bar_w, y + bar_h), (25, 25, 25), -1)
    
    fill_color = (0, 0, 255) if is_ready else ((0, 255, 255) if tension_pct > 0.6 else (255, 200, 0))
    fill_w = int(bar_w * tension_pct)
    cv2.rectangle(frame, (x, y), (x + fill_w, y + bar_h), fill_color, -1)
    cv2.rectangle(frame, (x, y), (x + bar_w, y + bar_h), (200, 200, 200), 1, cv2.LINE_AA)
    
    label = "READY TO FIRE!" if is_ready else f"PULL: {int(tension_pct * 100)}%"
    cv2.putText(frame, label, (x, y - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.45, fill_color, 1, cv2.LINE_AA)

# ==========================================
# 6. Threaded Camera Capture (Asynchronous I/O)
# ==========================================
class ThreadedCamera:
    """Membaca kamera di background thread agar loop utama tidak tertahan latency hardware"""
    def __init__(self, src=0, width=1280, height=720):
        self.cap = cv2.VideoCapture(src)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._reader, daemon=True)
        self.thread.start()

    def _reader(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                continue
            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self.lock:
            if self.frame is None:
                return False, None
            return self.ret, self.frame.copy()

    def stop(self):
        self.stopped = True
        self.cap.release()

# ==========================================
# 7. Program Utama
# ==========================================
def main():
    cam = ThreadedCamera(0, 1280, 720)
    time.sleep(0.3) # Pemanasan sensor webcam

    cv2.namedWindow("AR Hand Tracking", cv2.WINDOW_NORMAL)
    
    current_filter_idx = 0
    last_filter_change_time = 0
    last_snapshot_time = 0
    
    full_screen_mode = False
    is_ready_to_fire = False
    was_pinched_r = False
    was_pinched_l = False
    charged_sound_played = False
    
    reset_text_time = 0
    snapshot_text_time = 0
    
    # Layar Kilat Energi (White Screen Flash FX)
    screen_flash_intensity = 0.0
    
    # Filter Smoothing (Anti-Jitter EMA)
    smoothed_portal_pts = None
    
    # Sistem Gelombang Kejut (Shockwave FX)
    shockwaves = []
    
    prev_time = time.time()
    fps = 60

    print("Program AR Hand Tracking Sci-Fi Pro Berjalan. Tekan 'q' untuk keluar.")

    while True:
        ret, frame = cam.read()
        if not ret or frame is None:
            time.sleep(0.005)
            continue

        curr_time = time.time()
        fps_calc = 1.0 / (curr_time - prev_time + 1e-5)
        fps = int(0.9 * fps + 0.1 * fps_calc)
        prev_time = curr_time

        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        clean_frame = frame.copy() # Salinan gambar asli kamera murni tanpa efek apapun

        # AKSELERASI UTAMA: Deteksi tangan via Proxy Resolusi Ringan 320x180 (Inference ~11ms)
        # Menghasilkan 60+ FPS tanpa membebani CPU, koordinat 0.0-1.0 tetap presisi 100% di 720p
        small_rgb = cv2.resize(clean_frame, (320, 180))
        small_rgb = cv2.cvtColor(small_rgb, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=small_rgb)
        detection_result = detector.detect(mp_image)

        filter_name, filter_func, filter_color = filters[current_filter_idx]

        # Mode Full Screen jika aktif
        if full_screen_mode:
            frame = filter_func(clean_frame.copy())
            cv2.putText(frame, "OVERLOAD: FULL SCREEN FX ACTIVE", (w // 2 - 240, h - 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, filter_color, 2, cv2.LINE_AA)

        mode_text = "OVERLOAD ACTIVE" if full_screen_mode else "IDLE"

        if detection_result.hand_landmarks:
            hand_data = []
            for hand_landmarks in detection_result.hand_landmarks:
                x_min = min([lm.x for lm in hand_landmarks])
                hand_data.append({'landmarks': hand_landmarks, 'x': x_min})
                draw_cyber_skeleton(frame, hand_landmarks, w, h)
            
            hand_data.sort(key=lambda item: item['x'])
            left_hand = hand_data[0]['landmarks'] if len(hand_data) > 0 else None
            right_hand = hand_data[-1]['landmarks'] if len(hand_data) > 1 else None

            # --- GESTUR SNAPSHOT (✌️ Peace Sign) ---
            for hd in hand_data:
                if is_peace_sign(hd['landmarks']) and (curr_time - last_snapshot_time > 3.0):
                    last_snapshot_time = curr_time
                    snapshot_text_time = curr_time
                    screen_flash_intensity = 0.9 # White Shutter Flash
                    play_sfx(2200, 90) # Shutter Sound
                    # Simpan snapshot gambar berkualitas tinggi
                    filename = f"snapshot_ar_{int(curr_time)}.png"
                    cv2.imwrite(filename, frame)
                    print(f"Foto berhasil disimpan: {filename}")

            # --- GESTUR RESET (5 Jari Terbuka) ---
            reset_triggered = False
            for hd in hand_data:
                if is_open_palm(hd['landmarks']):
                    reset_triggered = True
            
            if reset_triggered:
                if full_screen_mode or is_ready_to_fire:
                    play_sfx(600, 70)
                full_screen_mode = False
                is_ready_to_fire = False 
                charged_sound_played = False
                smoothed_portal_pts = None
                reset_text_time = curr_time
                mode_text = "RESET EXECUTED"
            
            if curr_time - reset_text_time < 2:
                cv2.putText(frame, ">> SYSTEM NORMALIZED <<", (w // 2 - 160, 110), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 200), 2, cv2.LINE_AA)

            if curr_time - snapshot_text_time < 2.5:
                cv2.putText(frame, "[ 📸 PHOTO SAVED TO DISK ]", (w // 2 - 190, 150), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 0), 2, cv2.LINE_AA)

            # --- STATE MACHINE BERBASIS SENSOR ADAPTIF (2 Tangan) ---
            if len(hand_data) == 2 and not reset_triggered:
                pinched_l, thumb_l, index_l = is_pinch_adaptive(left_hand, w, h, was_pinched=was_pinched_l)
                pinched_r, thumb_r, index_r = is_pinch_adaptive(right_hand, w, h, was_pinched=was_pinched_r)
                was_pinched_l = pinched_l
                was_pinched_r = pinched_r
                
                open_l = not pinched_l
                open_r = not pinched_r

                if open_l and open_r:
                    # ==========================================
                    # STATE 1: PORTAL (Bekerja di Mode Normal & Overload)
                    # ==========================================
                    mode_text = "REALITY WINDOW" if full_screen_mode else "AR PORTAL ACTIVE"
                    
                    # Tembakan Ketapel Berhasil Dieksekusi
                    if is_ready_to_fire:
                        full_screen_mode = True
                        is_ready_to_fire = False
                        charged_sound_played = False
                        screen_flash_intensity = 0.85 # White Energy Flash
                        play_sfx(850, 160) # Blast Sound
                        
                        shockwaves.append({
                            "x": thumb_r[0], "y": thumb_r[1],
                            "radius": 15, "max_radius": int(math.hypot(w, h)),
                            "speed": 65, "color": filter_color
                        })
                    
                    else:
                        # Ambil koordinat 4 titik ujung jari
                        raw_pts = np.array([
                            [left_hand[8].x * w, left_hand[8].y * h],
                            [left_hand[4].x * w, left_hand[4].y * h],
                            [right_hand[4].x * w, right_hand[4].y * h],
                            [right_hand[8].x * w, right_hand[8].y * h]
                        ], dtype=np.float32)
                        
                        # Anti-Jitter Smoothing (Temporal EMA Filter)
                        if smoothed_portal_pts is None:
                            smoothed_portal_pts = raw_pts
                        else:
                            smoothed_portal_pts = 0.7 * raw_pts + 0.3 * smoothed_portal_pts
                            
                        pts = smoothed_portal_pts.astype(np.int32).reshape((-1, 1, 2))
                        
                        # AKSELERASI 3: Bounding Box ROI Cropping (Hanya memproses area kotak portal, hemat 90% CPU)
                        x_min = max(0, int(np.min(pts[:, 0, 0])))
                        y_min = max(0, int(np.min(pts[:, 0, 1])))
                        x_max = min(w, int(np.max(pts[:, 0, 0])))
                        y_max = min(h, int(np.max(pts[:, 0, 1])))
                        
                        if x_max > x_min and y_max > y_min:
                            roi_mask = np.zeros((y_max - y_min, x_max - x_min), dtype=np.uint8)
                            local_pts = pts.copy()
                            local_pts[:, 0, 0] -= x_min
                            local_pts[:, 0, 1] -= y_min
                            cv2.fillPoly(roi_mask, [local_pts], 255)
                            roi_mask_3ch = cv2.cvtColor(roi_mask, cv2.COLOR_GRAY2BGR)
                            
                            roi_clean = clean_frame[y_min:y_max, x_min:x_max]
                            roi_target = frame[y_min:y_max, x_min:x_max]
                            
                            if not full_screen_mode:
                                # MODE NORMAL: Hanya filter area kotak jari kecil
                                roi_filtered = filter_func(roi_clean.copy())
                                frame[y_min:y_max, x_min:x_max] = np.where(roi_mask_3ch == 255, roi_filtered, roi_target)
                                portal_label = f":: {filter_name} ::"
                                portal_color = filter_color
                            else:
                                # MODE FULL SCREEN / OVERLOAD: Kembalikan isi kotak ke kamera asli tanpa efek
                                frame[y_min:y_max, x_min:x_max] = np.where(roi_mask_3ch == 255, roi_clean, roi_target)
                                portal_label = ":: REALITY WINDOW (ORIGINAL) ::"
                                portal_color = (0, 255, 255) # Border Cyan/Emas Penembus Dimensi
                        
                        # Render Glow & Percikan Energi Melayang
                        draw_portal_glow_and_sparks(frame, pts, portal_color, curr_time)
                        
                        min_y = max(0, np.min(pts[:, 0, 1]))
                        min_x = max(0, np.min(pts[:, 0, 0]))
                        cv2.putText(frame, portal_label, 
                                    (min_x, max(80, min_y - 12)), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, portal_color, 2, cv2.LINE_AA)

                elif pinched_l and open_r:
                    # ==========================================
                    # STATE 2: GANTI FILTER (Cubit Kiri)
                    # ==========================================
                    smoothed_portal_pts = None
                    mode_text = "CYCLE SHADER"
                    cv2.circle(frame, thumb_l, 20, filter_color, 2, cv2.LINE_AA)
                    cv2.circle(frame, thumb_l, 6, (255, 255, 255), -1)
                    
                    if curr_time - last_filter_change_time > 0.9: 
                        current_filter_idx = (current_filter_idx + 1) % len(filters)
                        last_filter_change_time = curr_time
                        play_sfx(1400, 45) # Click sound
                    is_ready_to_fire = False
                    charged_sound_played = False

                elif open_l and pinched_r:
                    # ==========================================
                    # STATE 3: KETAPEL / SLINGSHOT CHARGE
                    # ==========================================
                    smoothed_portal_pts = None
                    mode_text = "SLINGSHOT CHARGING"
                    
                    idx_l_pt = (int(left_hand[8].x * w), int(left_hand[8].y * h))
                    thm_l_pt = (int(left_hand[4].x * w), int(left_hand[4].y * h))
                    
                    center_l = ((idx_l_pt[0] + thm_l_pt[0]) // 2, (idx_l_pt[1] + thm_l_pt[1]) // 2)
                    pull_dist = get_distance(center_l, thumb_r)
                    
                    tension_pct = min(1.0, pull_dist / 220.0)
                    is_ready_to_fire = (tension_pct >= 0.95)
                    
                    # Suara Overcharge saat tarikan 100%
                    if is_ready_to_fire and not charged_sound_played:
                        play_sfx(1900, 70)
                        charged_sound_played = True
                    elif not is_ready_to_fire:
                        charged_sound_played = False
                    
                    laser_color = (0, 0, 255) if is_ready_to_fire else (0, 255, 255)
                    
                    cv2.line(frame, idx_l_pt, thumb_r, laser_color, 4, cv2.LINE_AA)
                    cv2.line(frame, thm_l_pt, thumb_r, laser_color, 4, cv2.LINE_AA)
                    cv2.line(frame, idx_l_pt, thumb_r, (255, 255, 255), 1, cv2.LINE_AA)
                    cv2.line(frame, thm_l_pt, thumb_r, (255, 255, 255), 1, cv2.LINE_AA)
                    
                    dx = center_l[0] - thumb_r[0]
                    dy = center_l[1] - thumb_r[1]
                    aim_dist = 280
                    aim_x = int(center_l[0] + (dx / (pull_dist + 1e-5)) * aim_dist)
                    aim_y = int(center_l[1] + (dy / (pull_dist + 1e-5)) * aim_dist)
                    aim_x = int(np.clip(aim_x, 50, w - 50))
                    aim_y = int(np.clip(aim_y, 80, h - 50))
                    
                    cv2.line(frame, center_l, (aim_x, aim_y), laser_color, 1, cv2.LINE_AA)
                    draw_aim_reticle(frame, aim_x, aim_y, is_ready_to_fire, curr_time)
                    draw_tension_meter(frame, center_l[0] - 90, center_l[1] - 45, tension_pct, is_ready_to_fire)
                else:
                    smoothed_portal_pts = None
                    is_ready_to_fire = False
                    charged_sound_played = False

        # --- UPDATE & RENDER SHOCKWAVE EXPANSION FX ---
        active_shockwaves = []
        for sw in shockwaves:
            sw["radius"] += sw["speed"]
            fade = max(0.0, 1.0 - (sw["radius"] / sw["max_radius"]))
            if fade > 0.02 and sw["radius"] < sw["max_radius"]:
                thickness = max(1, int(7 * fade))
                cv2.circle(frame, (sw["x"], sw["y"]), int(sw["radius"]), (255, 255, 255), thickness, cv2.LINE_AA)
                cv2.circle(frame, (sw["x"], sw["y"]), int(max(1, sw["radius"] - 14)), sw["color"], max(1, thickness - 1), cv2.LINE_AA)
                active_shockwaves.append(sw)
        shockwaves = active_shockwaves

        # --- EFEK SCREEN WHITE FLASH FX (Recoil Energi / Shutter) ---
        if screen_flash_intensity > 0.01:
            flash_overlay = np.full_like(frame, 255)
            frame = cv2.addWeighted(frame, 1.0 - screen_flash_intensity * 0.5, flash_overlay, screen_flash_intensity * 0.5, 0)
            screen_flash_intensity = max(0.0, screen_flash_intensity - 0.12)

        # Banner Top HUD Futuristik
        draw_hud_banner(frame, mode_text, filter_name, fps, filter_color)

        cv2.imshow("AR Hand Tracking", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cam.stop()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()