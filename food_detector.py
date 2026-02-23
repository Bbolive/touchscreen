# -*- coding: utf-8 -*-
"""
โหลดโมเดล best.pt (YOLOv8) และวิเคราะห์ภาพเพื่อตรวจจับอาหาร
ดึงข้อมูลมาวิเคราะห์จากไฟล์โมเดลของ AI Food Recognition System Project
"""
import os

# โมเดลจะโหลดเมื่อมีการเรียกใช้ครั้งแรก (lazy load)
_model = None


def _get_model_path():
    from config import MODEL_PATH
    return MODEL_PATH


def is_available():
    m = load_model()
    print("MODEL LOADED:", m is not None)
    return m is not None


def load_model():
    """โหลดโมเดล YOLOv8 จาก best.pt"""
    global _model
    if _model is not None:
        return _model
    try:
        from ultralytics import YOLO
        path = _get_model_path()
        if not path or not os.path.isfile(path):
            return None
        _model = YOLO(path)
        return _model
    except Exception as e:
        print("Model load error:", e)
    return None



def detect(image_path=None, image_array=None, conf_threshold=None):
    """ วิเคราะห์ภาพด้วยโมเดล best.pt
    Args:
        image_path: path ไฟล์ภาพ (เช่น .jpg)
        image_array: numpy array ภาพ (RGB หรือ BGR) ถ้าไม่ใช้ image_path
        conf_threshold: ความมั่นใจขั้นต่ำ (ใช้จาก config ถ้าไม่ส่ง)

    Returns:
        list of dict: [
            {"label": "chicken_rice", "label_th": "ข้าวมันไก่", "confidence": 0.92, "price_per_unit": 45},
            ...
        ]
        เรียงจาก confidence สูงไปต่ำ
        ถ้าโหลดโมเดลไม่ได้หรือไม่มี detection คืน []
    """
    
    from config import CONFIDENCE_THRESHOLD, PRICE_PER_CLASS, CLASS_NAMES_TH

    model = load_model()
    if model is None:
        return []

    conf = conf_threshold if conf_threshold is not None else CONFIDENCE_THRESHOLD

    try:
        if image_path and os.path.isfile(image_path):
            results = model.predict(source=image_path, conf=conf, verbose=False)
        elif image_array is not None:
            results = model.predict(source=image_array, conf=conf, verbose=False)
        else:
            return []
    except Exception:
        return []

    if not results or len(results) == 0:
        return []

    boxes = results[0].boxes
    if boxes is None or len(boxes) == 0:
        return []

    # ชื่อคลาสจากโมเดล (อาจเรียงต่างจาก config)
    names = results[0].names or {}
    out = []
    for i in range(len(boxes)):
        cls_id = int(boxes.cls[i].item())
        conf_f = float(boxes.conf[i].item())
        label = names.get(cls_id, 'unknown')
        if isinstance(label, int):
            label = names.get(label, 'unknown')
        price = PRICE_PER_CLASS.get(label, 30)
        label_th = CLASS_NAMES_TH.get(label, label)
        out.append({
            'label': label,
            'label_th': label_th,
            'confidence': round(conf_f, 2),
            'price_per_unit': price,
        })

    # เรียง confidence สูงไปต่ำ
    out.sort(key=lambda x: -x['confidence'])
    return out


def detect_best(image_path=None, image_array=None, conf_threshold=None):
    """
    วิเคราะห์ภาพแล้วคืนชื่อเมนู (จากวัตถุดิบที่ตรวจจับได้) และราคา
    ถ้าแมปวัตถุดิบเป็นเมนูได้ (จาก MENU_DEFINITIONS) จะใช้ชื่อเมนูและราคาเมนู
    ถ้าแมปไม่ได้ จะใช้ชื่อวัตถุดิบรายการแรกและรวมราคาตาม PRICE_PER_CLASS
    """
    from config import ingredients_to_menu

    items = detect(image_path=image_path, image_array=image_array, conf_threshold=conf_threshold)
    if not items:
        return None
    best = items[0]
    detected_labels = [it['label'] for it in items]
    total_price_ingredients = sum(it['price_per_unit'] for it in items)

    menu_name, menu_price = ingredients_to_menu(items)
    if menu_name is not None and menu_price is not None:
        return {
            'label': menu_name,  # แสดงชื่อเมนูบนเว็บ
            'label_en': best['label'],
            'confidence': best['confidence'],
            'price_per_unit': menu_price,
            'total_detected': len(items),
            'total_price_sum': menu_price,
            'ingredients_detected': detected_labels,  # วัตถุดิบที่ตรวจจับได้ (ใช้แสดงบนภาพได้)
        }
    return {
        'label': best['label_th'],  # fallback: แสดงชื่อวัตถุดิบ
        'label_en': best['label'],
        'confidence': best['confidence'],
        'price_per_unit': best['price_per_unit'],
        'total_detected': len(items),
        'total_price_sum': total_price_ingredients,
        'ingredients_detected': detected_labels,
    }


def _draw_labels_on_image(image_path, boxes, names, names_th, confidences):
    """
    วาดกล่องและลาเบล (ชื่อวัตถุดิบภาษาไทย เช่น ไก่ ข้าว แตงกวา) บนภาพ แล้วคืน base64
    boxes: tensor หรือ list ของ [x1,y1,x2,y2]
    names: dict cls_id -> label_en
    names_th: dict label_en -> label_th (เช่น rice->ข้าว, cucumber->แตงกวา, fried_chicken->ไก่ทอด)
    """
    import base64
    import io
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return None

    try:
        img = Image.open(image_path).convert('RGB')
    except Exception:
        return None

    draw = ImageDraw.Draw(img)
    w, h = img.size
    font_size = max(14, min(w, h) // 25)

    # ลองโหลดฟอนต์ภาษาไทย (Windows/Linux/macOS)
    font = None
    for path in [
        'C:/Windows/Fonts/leelawad.ttf',
        'C:/Windows/Fonts/thsarabunnew.ttf',
        'C:/Windows/Fonts/THSarabun.ttf',
        'C:/Windows/Fonts/tahoma.ttf',
        '/usr/share/fonts/truetype/thai/Garuda.ttf',
        '/usr/share/fonts/truetype/fonts-thai-tlwg/TlwgMono.ttf',
        '/System/Library/Fonts/Supplemental/Arial Unicode.ttf',
    ]:
        if os.path.isfile(path):
            try:
                font = ImageFont.truetype(path, font_size)
                break
            except Exception:
                pass
    if font is None:
        try:
            font = ImageFont.load_default()
        except Exception:
            font = None

    box_color = (16, 185, 129)
    text_bg = (16, 185, 129)
    text_color = (255, 255, 255)
    label_h = max(18, min(w, h) // 20)

    for i in range(len(boxes)):
        try:
            xy = boxes.xyxy[i]
            if hasattr(xy, 'cpu'):
                xy = xy.cpu().numpy()
            x1 = int(round(float(xy[0])))
            y1 = int(round(float(xy[1])))
            x2 = int(round(float(xy[2])))
            y2 = int(round(float(xy[3])))
            cls_id = int(boxes.cls[i].item()) if hasattr(boxes.cls[i], 'item') else int(boxes.cls[i])
            conf = confidences[i] if i < len(confidences) else 0
            label_en = names.get(cls_id, 'unknown')
            if isinstance(label_en, int):
                label_en = names.get(label_en, 'unknown')
            # ใช้ชื่อภาษาไทย (วัตถุดิบ): ข้าว แตงกวา ไก่ทอด ฯลฯ
            label_th = names_th.get(label_en, label_en)
            text = '{} {:.0%}'.format(label_th, conf)
        except Exception:
            continue

        draw.rectangle([x1, y1, x2, y2], outline=box_color, width=max(2, min(w, h) // 200))
        ty0 = max(0, y1 - label_h)
        draw.rectangle([x1, ty0, x2, y1], fill=text_bg)
        if font:
            draw.text((x1, ty0), text, fill=text_color, font=font)
        else:
            draw.text((x1, ty0), text, fill=text_color)

    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=88)
    return base64.b64encode(buf.getvalue()).decode('utf-8')


def detect_best_with_annotated_image(image_path, conf_threshold=None):
    """
    วิเคราะห์ภาพ แล้วคืน (result สำหรับแสดงชื่อ/ราคา, ภาพที่วาด label แล้วเป็น base64)
    result รูปแบบเดียวกับ detect_best; ภาพมีกล่องและลาเบลชื่ออาหาร (ไทย) ที่ตำแหน่งที่ตรวจจับได้
    """
    from config import CONFIDENCE_THRESHOLD, CLASS_NAMES_TH

    model = load_model()
    if model is None or not image_path or not os.path.isfile(image_path):
        return None, None

    conf = conf_threshold if conf_threshold is not None else CONFIDENCE_THRESHOLD
    try:
        results = model.predict(source=image_path, conf=conf, verbose=False)
    except Exception:
        return None, None

    if not results or len(results) == 0:
        return None, None

    boxes = results[0].boxes
    names = results[0].names or {}
    if boxes is None or len(boxes) == 0:
        return None, None

    best_result = detect_best(image_path=image_path, conf_threshold=conf)
    confidences = [float(boxes.conf[i].item()) for i in range(len(boxes))]
    annotated_b64 = _draw_labels_on_image(image_path, boxes, names, CLASS_NAMES_TH, confidences)

    # ถ้าวาดลาเบลภาษาไทยไม่ได้ ใช้ภาพที่ ultralytics วาด (ภาษาอังกฤษ)
    if not annotated_b64:
        try:
            import base64
            import io
            plotted = results[0].plot()
            if len(plotted.shape) == 3 and plotted.shape[2] == 3:
                plotted = plotted[:, :, ::-1]
            from PIL import Image
            img = Image.fromarray(plotted)
            buf = io.BytesIO()
            img.save(buf, format='JPEG', quality=88)
            annotated_b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        except Exception:
            pass

    return best_result, annotated_b64
