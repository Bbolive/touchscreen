# ระบบตรวจจับอาหารอัตโนมัติ – หน้าจอทัชสกรีน

เว็บแอปสำหรับแสดงบนจอทัชสกรีน 7 นิ้วของ Raspberry Pi ใช้กับ **Pi Camera**, **Loadcell + HX711** และบอร์ด Raspberry Pi

## หน้าจอ

1. **หน้าก่อนตรวจจับ**
   - แสดงสถานะกล้อง (พร้อม/ไม่พร้อม)
   - ขั้นตอนการใช้งาน 4 ขั้น
   - น้ำหนักแบบสดจาก Loadcell (อัปเดตทุก 1.5 วินาที)
   - ปุ่ม **เริ่มตรวจจับ** (กดได้เมื่อกล้องพร้อม)

2. **หน้ารзультаลัพธ์**
   - ชนิดอาหารที่ตรวจจับได้
   - ความมั่นใจ (confidence)
   - น้ำหนักจาก Loadcell (กรัม)
   - ราคาที่คำนวณ (บาท)
   - ปุ่ม **ตรวจจับใหม่** กลับไปหน้าก่อน

## การติดตั้ง

### บน Windows (สำหรับพัฒนา/ทดสอบ)

```bash
cd touchscreen
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

เปิดเบราว์เซอร์ที่ `http://127.0.0.1:5000`

### บน Raspberry Pi (จอ 7 นิ้ว)

1. ติดตั้ง Python 3 และ pip แล้วสร้าง virtualenv:

```bash
cd touchscreen
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. (ถ้าใช้ Pi Camera จริง) ติดตั้ง picamera2:

```bash
sudo apt update
sudo apt install -y python3-picamera2
```

3. (ถ้าใช้ Loadcell + HX711 จริง) ติดตั้งไลบรารี HX711 และเปิด SPI/GPIO ตามบอร์ดที่ใช้ เช่น:

```bash
pip install hx711  # หรือใช้ repo ที่รองรับ RPi.GPIO
```

4. รันเซิร์ฟเวอร์:

```bash
python3 app.py
```

5. เปิด Chromium ในโหมด Kiosk เต็มจอ (แนะนำสำหรับจอ 7 นิ้ว):

```bash
chromium-browser --kiosk --noerrdialogs --disable-infobars http://127.0.0.1:5000
```

หรือเพิ่มเป็น autostart เมื่อเปิด Pi (ดูไฟล์ `autostart-touchscreen.sh` ด้านล่าง)

---

## ใช้เว็บบน Pi Touchscreen ได้ไหม?

**ได้ครับ** โปรเจกต์นี้เป็น **เว็บแอป** อยู่แล้ว เหมาะกับการใช้บนจอทัชสกรีนของ Pi โดยตรง:

1. **รัน Flask บน Pi** → เซิร์ฟเวอร์ให้หน้าเว็บที่ `http://127.0.0.1:5000`
2. **เปิด Chromium บน Pi** → เปิด URL นี้บนจอทัชสกรีน จะได้ทั้งแสดงผลและกด (touch) ใช้งานได้
3. **โหมด Kiosk** → ใช้ `chromium-browser --kiosk ...` จะได้เต็มจอ ไม่มีแถบ URL/ปุ่มเบราว์เซอร์ เหลือแค่หน้าของเรา

ข้อดีของแบบเว็บบน Touchscreen Pi:
- ใช้จอ 7 นิ้วเป็นจอหลัก แสดงผลและรับคำสั่งจาก touch ได้
- อัปเดตแก้หน้าเว็บได้โดยไม่ต้องลงแอปใหม่
- พัฒนา/ทดบน Windows ได้ แล้วค่อยเอาโฟลเดอร์ไปรันบน Pi

## Autostart บน Pi (เปิดเว็บเต็มจอเมื่อเปิดเครื่อง)

1. คัดลอกหรือสร้างสคริปต์ `autostart-touchscreen.sh` (อยู่ในโฟลเดอร์โปรเจกต์)
2. ทำให้รันได้: `chmod +x autostart-touchscreen.sh`
3. ใส่ใน autostart ของ Pi ได้สองแบบ:
   - **แบบ Desktop (เมื่อเข้า Desktop):** สร้างไฟล์ `~/.config/autostart/touchscreen.desktop` เนื้อหาตามนี้ (แก้ `PATH_TO_PROJECT` ให้เป็น path จริง):
     ```ini
     [Desktop Entry]
     Type=Application
     Name=Touchscreen Food Detection
     Exec=/bin/bash -c "cd PATH_TO_PROJECT && ./autostart-touchscreen.sh"
     ```
   - **แบบ systemd:** สร้าง service รัน `python3 app.py` แล้วให้ Chromium เปิดหลัง boot (หรือใช้สคริปต์รวมใน ExecStart)

## การต่อฮาร์ดแวร์

- **Pi Camera**: ต่อกับ CSI ของ Raspberry Pi และเปิด Camera ใน `raspi-config` (Interface Options → Camera).
- **HX711 + Loadcell**: ต่อ DT และ SCK ของ HX711 กับ GPIO (ใน `app.py` ใช้ dout_pin=5, pd_sck_pin=6 เป็นค่าเริ่มต้น – แก้ในฟังก์ชัน `get_weight_gram()` ให้ตรงกับบอร์ดจริง).

## การดึงข้อมูลมาวิเคราะห์ด้วยโมเดล best.pt (YOLOv8)

โปรเจกต์รองรับการโหลดโมเดลจาก **AI Food Recognition System Project** (ไฟล์ `best.pt`) เพื่อวิเคราะห์ภาพจริง:

1. **ตั้งค่า path โมเดล** ใน `config.py` ตัวแปร `MODEL_PATH` (หรือตั้ง environment `FOOD_MODEL_PATH`)
2. **ติดตั้ง dependencies สำหรับ ML**:  
   `pip install -r requirements-ml.txt`  
   (จะติดตั้ง ultralytics, torch, torchvision)
3. วางไฟล์ `best.pt` ไว้ที่ path ที่กำหนด หรือคัดลอกไปที่โฟลเดอร์โปรเจกต์แล้วชี้ `MODEL_PATH` ไปที่ไฟล์นั้น

เมื่อมีภาพ (จาก Pi Camera หรือการอัปโหลด) ระบบจะส่งภาพเข้าโมเดลและใช้ผลตรวจจับ (18 คลาสอาหาร) แทนโหมดจำลอง ชื่อคลาสและราคาต่อคลาสแก้ได้ใน `config.py` (`CLASS_NAMES_TH`, `PRICE_PER_CLASS`)

## โหมดจำลอง

เมื่อรันบน Windows หรือเมื่อไม่มี Pi Camera / HX711 ติดตั้ง หรือยังไม่ได้ติดตั้ง ultralytics/โมเดล ระบบจะใช้โหมดจำลอง:

- สถานะกล้อง: แสดง "กล้องพร้อม (โหมดจำลอง)"
- น้ำหนัก: 0.0 g
- การตรวจจับ: สุ่มชนิดอาหารจากรายการใน `MOCK_FOOD_PRICES`

## แก้ไขราคาอาหาร

แก้ใน `app.py` ที่ตัวแปร `MOCK_FOOD_PRICES` (และใช้ชุดเดียวกันสำหรับการตรวจจับจริงเมื่อมีโมเดล ML).

## ความละเอียดจอ

ออกแบบสำหรับความละเอียดประมาณ **800×480** หรือ **1024×600** (จอ 7 นิ้ว) และปุ่มขนาดใหญ่พอสำหรับการสัมผัส
