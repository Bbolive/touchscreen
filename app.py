# -*- coding: utf-8 -*-
"""
ระบบตรวจจับอาหารอัตโนมัติ - เซิร์ฟเวอร์หลัก
รองรับ Pi Camera, Loadcell (HX711), Raspberry Pi
"""
import os
import sys

# รองรับการรันบน Windows (พัฒนา) และ Linux (Pi)
HX711 = None
Picamera2 = None
if sys.platform == 'linux':
    try:
        from picamera2 import Picamera2
    except ImportError:
        pass
    try:
        from hx711 import HX711
    except ImportError:
        pass

from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__, static_folder='static', template_folder='templates')

# --- จำลองข้อมูล (ใช้เมื่อไม่มีฮาร์ดแวร์จริง) ---
MOCK_CAMERA_READY = True
MOCK_WEIGHT_GRAM = 0.0
MOCK_FOOD_PRICES = {
    'ก๋วยเตี๋ยว': 40,
    'ผัดกะเพรา': 45,
    'ข้าวมันไก่': 50,
}


def get_camera_status():
    """สถานะกล้อง Pi Camera"""
    if Picamera2 is not None:
        try:
            cam = Picamera2()
            cam.start()
            cam.stop()
            return {'ready': True, 'message': 'กล้องพร้อมใช้งาน', 'source': 'real'}
        except Exception as e:
            return {'ready': False, 'message': str(e), 'source': 'real'}
    return {
        'ready': MOCK_CAMERA_READY,
        'message': 'กล้องพร้อม (โหมดจำลอง)' if MOCK_CAMERA_READY else 'กล้องไม่พร้อม',
        'source': 'mock',
    }


def get_weight_gram():
    """น้ำหนักจาก Loadcell + HX711 (กรัม)"""
    if HX711 is not None:
        try:
            # ปรับ pin ตามการต่อบอร์ดจริง (DT, SCK)
            hx = HX711(dout_pin=5, pd_sck_pin=6)
            hx.set_reading_format("MSB", "MSB")
            hx.set_reference_unit(1)  # แคลิเบรตตาม loadcell จริง
            hx.reset()
            val = hx.get_weight(5)
            hx.power_down()
            hx.power_up()
            return max(0.0, float(val or 0))
        except Exception:
            pass
    return MOCK_WEIGHT_GRAM


def run_detection_mock():
    """จำลองผลตรวจจับอาหาร (แทนโมเดล ML จริง)"""
    import random
    names = list(MOCK_FOOD_PRICES.keys())
    if names and names[0] != 'unknown':
        names = [n for n in names if n != 'unknown']
    chosen = random.choice(names) if names else 'unknown'
    return {
        'label': chosen,
        'confidence': round(random.uniform(0.85, 0.99), 2),
        'price_per_unit': MOCK_FOOD_PRICES.get(chosen, 30),
    }


def capture_image_to_file():
    """ถ่ายภาพจาก Pi Camera เก็บเป็นไฟล์ชั่วคราว คืน (path, base64) หรือ (None, None)"""
    if Picamera2 is None:
        return None, None
    try:
        import base64
        import tempfile
        cam = Picamera2()
        config = cam.create_still_configuration()
        cam.configure(config)
        cam.start()
        import time
        time.sleep(0.5)
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
            path = f.name
        try:
            cam.capture_file(path)
            cam.stop()
            with open(path, 'rb') as f:
                b64 = base64.b64encode(f.read()).decode('utf-8')
            return path, b64
        except Exception:
            if os.path.exists(path):
                os.unlink(path)
            return None, None
    except Exception:
        return None, None


# --- API ---

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/camera/status')
def api_camera_status():
    return jsonify(get_camera_status())


@app.route('/api/weight')
def api_weight():
    w = get_weight_gram()
    return jsonify({'weight_gram': round(w, 1), 'unit': 'g'})


def _resize_image_base64_for_display(b64_string, max_size=1200, quality=85):
    """ย่อภาพให้เหมาะกับการแสดงบนมือถือ (ลดขนาด data URL เพื่อให้ label แสดงได้)"""
    if not b64_string:
        return b64_string
    try:
        import base64
        from PIL import Image
        import io
        raw = base64.b64decode(b64_string)
        img = Image.open(io.BytesIO(raw)).convert('RGB')
        w, h = img.size
        if max(w, h) > max_size:
            ratio = max_size / max(w, h)
            new_w = int(w * ratio)
            new_h = int(h * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=quality)
        return base64.b64encode(buf.getvalue()).decode('utf-8')
    except Exception:
        return b64_string


@app.route('/api/detect', methods=['POST'])
def api_detect():
    """ถ่ายภาพ (ถ้ามีกล้อง) หรือรับภาพอัปโหลด แล้วดึงข้อมูลมาวิเคราะห์ด้วย best.pt หรือโหมดจำลอง
    ถ้าไม่มีภาพจากกล้องและไม่ได้อัปโหลด → ใช้ผลจำลอง (mock) ให้เสมอ ไม่ให้ตรวจจับไม่เจอ"""
    image_path = None
    image_base64 = None

    # ภาพจากไฟล์อัปโหลด หรือจากกล้อง Pi
    if request.files and request.files.get('image'):
        import base64
        import tempfile
        f = request.files['image']
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            f.save(tmp.name)
            image_path = tmp.name
        with open(image_path, 'rb') as rf:
            image_base64 = base64.b64encode(rf.read()).decode('utf-8')
    else:
        image_path, image_base64 = capture_image_to_file()

    # มีภาพ → วิเคราะห์ด้วยโมเดล (หรือ mock ถ้าโมเดลไม่ทำงาน); ไม่มีภาพ → ใช้ mock เสมอ
    detection = None
    total_price = 0.0
    if image_path:
        try:
            from food_detector import is_available, detect_best_with_annotated_image
            if is_available():
                result, annotated_base64 = detect_best_with_annotated_image(image_path)
                if result:
                    total_price = result.get('total_price_sum') or result['price_per_unit']
                    detection = {
                        'label': result['label'],
                        'confidence': result['confidence'],
                        'price_per_unit': result['price_per_unit'],
                    }
                    if annotated_base64:
                        image_base64 = annotated_base64
        except Exception:
            pass
        if image_path and os.path.exists(image_path):
            try:
                os.unlink(image_path)
            except Exception:
                pass
        if image_base64:
            image_base64 = _resize_image_base64_for_display(image_base64)

    no_image = image_path is None
    if detection is None:
        detection = run_detection_mock()
        total_price = detection['price_per_unit']

    weight = get_weight_gram()
    return jsonify({
        'detection': detection,
        'weight_gram': round(weight, 1),
        'total_price_bath': total_price,
        'timestamp': datetime.now().isoformat(),
        'image_base64': image_base64,
        'no_image': no_image,
    })


@app.route('/api/config/prices', methods=['GET'])
def api_prices():
    return jsonify(MOCK_FOOD_PRICES)


if __name__ == '__main__':
    # สำหรับจอ 7 นิ้ว ใช้ 0.0.0.0 เพื่อให้เข้าได้จากอุปกรณ์อื่น
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
