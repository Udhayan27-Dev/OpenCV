import cv2

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

if not cap.isOpened():
    print("Error: Could not open webcam.")
    exit()

print("Controls: Press 's' to save a frame, 'q' to quit.")

frame_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    cv2.imshow("Webcam Live Preview", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord('s'):
        filename = f"capture_{frame_count}.jpg"
        cv2.imwrite(filename, frame)
        print(f"Saved: {filename}")
        frame_count += 1
    elif key == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
