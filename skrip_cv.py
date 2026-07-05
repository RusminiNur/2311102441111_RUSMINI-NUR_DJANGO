import cv2
import mediapipe as mp

# 1. Mengaktifkan fitur deteksi wajah (Face Mesh) dari MediaPipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(max_num_faces=1, refine_landmarks=True)

# 2. Mengaktifkan Kamera/Webcam laptop
cap = cv2.VideoCapture(0)

print("Program berjalan... Tekan tombol 'ESC' pada keyboard untuk keluar.")

while cap.isOpened():
    success, frame = cap.read()
    if not success:
        print("Kamera tidak merespon.")
        continue

    # Ubah warna dari BGR ke RGB untuk MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Proses gambar untuk mendeteksi wajah
    hasil_deteksi = face_mesh.process(rgb_frame)

    # JIKA wajah terdeteksi, ambil koordinatnya
    if hasil_deteksi.multi_face_landmarks:
        for face_landmarks in hasil_deteksi.multi_face_landmarks:
            
            # Daftar indeks titik penting wajah:
            # 1 = Hidung, 33 = Mata Kiri, 263 = Mata Kanan, 61 = Bibir Kiri, 291 = Bibir Kanan
            titik_penting = [1, 33, 263, 61, 291]
            
            tinggi_layar, lebar_layar, _ = frame.shape
            
            for indeks in titik_penting:
                landmark = face_landmarks.landmark[indeks]
                
                # Ubah ke koordinat pixel layar
                pixel_x = int(landmark.x * lebar_layar)
                pixel_y = int(landmark.y * tinggi_layar)
                
                # Gambar lingkaran hijau di setiap titik penting tersebut
                cv2.circle(frame, (pixel_x, pixel_y), 5, (0, 255, 0), -1)
                
            # Cetak teks di layar video sebagai info
            cv2.putText(frame, "Tracking 5 Titik Utama Wajah", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # Tampilkan jendela video kamera
    cv2.imshow('Kamera Anggota 1 - CV Tracking', frame)

    # Jika menekan tombol ESC, program berhenti
    if cv2.waitKey(5) & 0xFF == 27:
        break

# Matikan kamera dan tutup jendela program
cap.release()
cv2.destroyAllWindows()