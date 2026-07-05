import cv2
import mediapipe as mp
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *

# ==============================================================================
# 1. INISIALISASI SISTEM (PENGGABUNGAN PIPELINE CV & CG)
# ==============================================================================

# [BAGIAN VISI KOMPUTER] - Setup Ekstraksi Fitur Citra Face Mesh
# Mengaktifkan deteksi wajah berbasis Machine Learning (MediaPipe)
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)
cap = cv2.VideoCapture(0) # Mengambil input video stream dari webcam

# [BAGIAN KOMPUTER GRAFIK] - Setup Windowing & Graphics Pipeline
# Menginisialisasi Pygame sebagai konteks window manager untuk OpenGL
pygame.init()
tampilan_3d = (600, 600)
pygame.display.set_mode(tampilan_3d, DOUBLEBUF | OPENGL)
pygame.display.set_caption("Jendela CG - Advanced 3D Face Mesh")

# [BAGIAN KOMPUTER GRAFIK] - Pengaturan Perspektif Kamera 3D
# Mengatur Field of View (45 derajat), Aspect Ratio, Near-Z, dan Far-Z
gluPerspective(45, (tampilan_3d[0] / tampilan_3d[1]), 0.1, 50.0)
glTranslatef(0.0, 0.0, -3.0) # Transformasi Translasi: Mundurkan objek agar masuk viewing frustum

# [BAGIAN VISI KOMPUTER] - Indeks Fitur Semantik Wajah (17 Titik Utama)
# Menentukan indeks koordinat spesifik berdasarkan topologi MediaPipe Face Mesh
indeks_cv = [
    10,  # 0: Dahi Atas          13: Alis Kiri Atas  -> 70
    152, # 1: Dagu Bawah         14: Alis Kanan Atas -> 300
    234, # 2: Pipi Kiri Luar     15: Batang Hidung   -> 4
    454, # 3: Pipi Kanan Luar    16: Tengah Mata     -> 168
    1,   # 4: Ujung Hidung
    33,  # 5: Mata Kiri Luar
    133, # 6: Mata Kiri Dalam
    362, # 7: Mata Kanan Dalam
    263, # 8: Mata Kanan Luar
    61,  # 9: Sudut Bibir Kiri
    291, # 10: Sudut Bibir Kanan
    0,   # 11: Bibir Atas Tengah
    17,  # 12: Bibir Bawah Tengah
    70,  
    300, 
    4,   
    168  
]

# [BAGIAN KOMPUTER GRAFIK] - Alokasi Memori Vertices Objek 3D
# Menyiapkan matriks berukuran 17x3 untuk menampung posisi Vertex (X, Y, Z)
vertices_3d = np.zeros((len(indeks_cv), 3), dtype=np.float32)

# [BAGIAN KOMPUTER GRAFIK] - Topologi Geometri (Daftar Edges / Garis)
# Menentukan pasangan vertex mana saja yang harus dihubungkan oleh Primitive OpenGL
garis_topeng = [
    (0, 13), (0, 14),           # Hubungan Dahi ke Alis
    (13, 16), (14, 16),         # Hubungan Alis ke Tengah Mata
    (16, 15), (15, 4),          # Hubungan Tengah Mata ke Batang Hidung
    (5, 6), (7, 8),             # Struktur Mata Kiri & Kanan
    (2, 5), (3, 8),             # Hubungan Struktur Pipi Luar ke Mata
    (2, 9), (3, 10),            # Hubungan Pipi ke Sudut Bibir
    (9, 11), (11, 10),          # Kontur Bibir Atas
    (9, 12), (12, 10),          # Kontur Bibir Bawah
    (4, 11),                    # Hubungan Jangkar Hidung ke Bibir
    (9, 1), (10, 1)             # Hubungan Sudut Bibir ke Dagu Bawah
]

print("Aplikasi Integrasi CV-CG Berjalan Aktif...")

# ==============================================================================
# 2. ITERASI UTAMA (SINKRONISASI REAL-TIME FRAME-BY-FRAME)
# ==============================================================================
running = True
while running:
    # Mengosongkan antrean event Pygame agar jendela tidak beku (freeze)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    success, frame = cap.read()
    if not success: 
        break

    # [BAGIAN VISI KOMPUTER] - Preprocessing Citra Digital
    # 1. Transformasi Geometri: Flip horizontal untuk memicu efek cermin (Mirroring)
    frame = cv2.flip(frame, 1)
    # 2. Konversi Ruang Warna: Mengubah BGR (OpenCV) menjadi RGB (MediaPipe)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # 3. Pemrosesan Kognisi: Deteksi fitur wajah secara matematis
    hasil_deteksi = face_mesh.process(rgb_frame)

    sedang_senyum = False # Bendera boolean untuk klasifikasi ekspresi

    if hasil_deteksi.multi_face_landmarks:
        for face_landmarks in hasil_deteksi.multi_face_landmarks:
            tinggi, lebar, _ = frame.shape
            
            # [BAGIAN VISI KOMPUTER] - Analisis Citra (Deteksi Ekspresi)
            # Mengekstrak posisi spasial sudut bibir kiri (61) dan kanan (291)
            bibir_kiri = face_landmarks.landmark[61]
            bibir_kanan = face_landmarks.landmark[291]
            
            # Perhitungan Jarak Euclidean (Matematika Viskom)
            jarak_bibir = np.sqrt((bibir_kiri.x - bibir_kanan.x)**2 + (bibir_kiri.y - bibir_kanan.y)**2)
            
            # Thresholding: Jika jarak melebihi batas piksel ternormalisasi, status = Senyum
            if jarak_bibir > 0.09: 
                sedang_senyum = True
            
            # [BAGIAN VISI KOMPUTER & KOMPUTER GRAFIK] - Jembatan Pemetaan Koordinat
            for i, idx in enumerate(indeks_cv):
                landmark = face_landmarks.landmark[idx]
                
                # Visualisasi Validasi Internal Viskom (Menggambar titik hijau di kamera)
                px = int(landmark.x * lebar)
                py = int(landmark.y * tinggi)
                cv2.circle(frame, (px, py), 3, (0, 255, 0), -1)
                
                # Formula Normalisasi & Pemetaan ke Sistem Koordinat Kartesian OpenGL
                vertices_3d[i][0] = (landmark.x - 0.5) * 2.5   # Sumbu X (Translasi ke titik tengah)
                vertices_3d[i][1] = -(landmark.y - 0.5) * 2.5  # Sumbu Y (Inversi sumbu vertikal)
                vertices_3d[i][2] = -landmark.z * 3            # Sumbu Z (Proyeksi kedalaman/Depth)

    # ==============================================================================
    # 3. PIPELINE RENDERING INTERAKTIF (SISI KOMPUTER GRAFIK)
    # ==============================================================================
    # Mengosongkan Frame Buffer dan Depth Buffer sebelum merender objek baru
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    
    # Manipulasi Warna Primitives Berdasarkan State Interaksi Ekspresi (Kondisional)
    if sedang_senyum:
        glColor3f(0.0, 1.0, 0.0) # Mengubah kuas OpenGL menjadi Hijau (Senyum)
        cv2.putText(frame, "STATUS: SENYUM", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    else:
        glColor3f(0.0, 1.0, 1.0) # Mengubah kuas OpenGL menjadi Cyan (Biasa)
        cv2.putText(frame, "STATUS: BIASA", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    # Rasterisasi Garis: Menggambar struktur Edges Topeng 3D
    glLineWidth(2)
    glBegin(GL_LINES) # Primitives Mode: Garis Independen
    for sambungan in garis_topeng:
        glVertex3fv(vertices_3d[sambungan[0]]) # Mengirim posisi awal Vertex 3D
        glVertex3fv(vertices_3d[sambungan[1]]) # Mengirim posisi akhir Vertex 3D
    glEnd()

    # Rasterisasi Titik: Menggambar posisi Vertices di setiap persimpangan
    glPointSize(6)
    glBegin(GL_POINTS) # Primitives Mode: Titik Tunggal
    glColor3f(1.0, 0.0, 0.0) # Mewarnai setiap simpul dengan warna Merah
    for vertex in vertices_3d:
        glVertex3fv(vertex)
    glEnd()

    # Double Buffering: Menukar buffer belakang (render) ke buffer depan (layar monitor)
    pygame.display.flip()
    pygame.time.wait(10) # Mengatur frame rate limiter singkat

    # [BAGIAN VISI KOMPUTER] - Rendering Overlay Teks Informasi pada Gambar Kamera
    cv2.putText(frame, "Advanced 17-Points Tracking", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.imshow('Jendela CV - Tracking Kamera', frame)

    # Terminasi aplikasi secara aman via Interupsi Keyboard (Tombol ESC)
    if cv2.waitKey(5) & 0xFF == 27:
        break

# Melepaskan alokasi memori hardware secara bersih (Cleanup)
cap.release()
cv2.destroyAllWindows()
pygame.quit()