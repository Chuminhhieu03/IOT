import cv2
import paho.mqtt.client as mqtt
import base64
import time
import os
from dotenv import load_dotenv

load_dotenv()

# Cấu hình thông tin MQTT
MQTT_BROKER = os.environ.get("MQTT_BROKER")  # Địa chỉ của MQTT broker (thay bằng địa chỉ của bạn)
MQTT_PORT = 8883                    # Cổng của MQTT broker
MQTT_TOPIC = "face-recognition/image"         # Chủ đề để gửi ảnh (thay đổi theo yêu cầu)
MQTT_USERNAME = os.environ.get("MQTT_USERNAME")  # Username của MQTT broker
MQTT_PASSWORD = os.environ.get("MQTT_PASSWORD")  # Password của MQTT broker


# Khởi tạo MQTT client
client = mqtt.Client()

client.tls_set(tls_version=mqtt.ssl.PROTOCOL_TLS)
client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
# Kết nối tới MQTT Broker
client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
print(f"Đã kết nối tới MQTT broker: {MQTT_BROKER}")

# Hàm chuyển đổi ảnh thành base64
def image_to_base64(image):
    _, buffer = cv2.imencode('.jpg', image)   # Chuyển đổi ảnh thành buffer dạng jpg
    image_bytes = base64.b64encode(buffer)    # Chuyển buffer thành base64
    return image_bytes

# Mở camera (camera mặc định là 0)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Không thể mở camera.")
    exit()

try:
    while True:
        # Đọc từng khung hình từ camera
        ret, frame = cap.read()
        if not ret:
            print("Không thể lấy khung hình từ camera.")
            break

        # Chuyển đổi khung hình thành chuỗi base64
        image_base64 = image_to_base64(frame).decode('utf-8')  # Chuyển đổi thành chuỗi utf-8

        # Gửi ảnh đã mã hóa lên chủ đề MQTT
        client.publish(MQTT_TOPIC, image_base64)
        print(f"Đã gửi ảnh lên MQTT: {MQTT_TOPIC}")

        # Đợi 1 giây trước khi chụp tiếp (để giảm tải)
        time.sleep(0.5)

        # Hiển thị khung hình
        cv2.imshow("Camera", frame)

        # Thoát chương trình nếu nhấn phím 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

except KeyboardInterrupt:
    print("Đã dừng chương trình.")

finally:
    # Giải phóng tài nguyên
    cap.release()
    cv2.destroyAllWindows()
    client.disconnect()
    print("Đã giải phóng camera và ngắt kết nối MQTT.")
