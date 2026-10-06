import cv2
import time

print("[1/5] Initializing camera...")
# Try index 0 with V4L2 backend
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

print("[2/5] Checking if camera opened...")
if not cap.isOpened():
    print("ERROR: Camera failed to open at /dev/video0.")
    exit(1)

print("[3/5] Camera opened successfully. Reading first test frame...")
ret, frame = cap.read()
if not ret:
    print("ERROR: Could not read a frame from camera.")
    cap.release()
    exit(1)

print("[4/5] Frame grabbed successfully! Starting display loop...")

TARGET_FPS = 15
FRAME_TIME = 1.0 / TARGET_FPS
prev_frame_time = time.time()
actual_fps = 0.0

while True:
    frame_start = time.time()
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY_INV, 11, 2
    )

    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    display_frame = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    object_count = 0
    for cnt in contours:
        if cv2.contourArea(cnt) > 1200:
            object_count += 1
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(display_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    latency_ms = (time.time() - frame_start) * 1000.0
    cur_t = time.time()
    delta = cur_t - prev_frame_time
    if delta > 0:
        actual_fps = 0.9 * actual_fps + 0.1 * (1.0 / delta)
    prev_frame_time = cur_t

    cv2.rectangle(display_frame, (10, 10), (240, 115), (30, 30, 30), -1)
    cv2.rectangle(display_frame, (10, 10), (240, 115), (0, 255, 255), 1)
    cv2.putText(display_frame, f"FPS: {actual_fps:.1f} / {TARGET_FPS}", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    cv2.putText(display_frame, f"Latency: {latency_ms:.1f} ms", (20, 65),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 0), 1)
    cv2.putText(display_frame, f"Objects: {object_count}", (20, 95),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 255), 1)

    cv2.imshow("Grayscale Stream", display_frame)

    elapsed = time.time() - frame_start
    wait_ms = max(1, int((FRAME_TIME - elapsed) * 1000)) if FRAME_TIME > elapsed else 1

    if cv2.waitKey(wait_ms) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
