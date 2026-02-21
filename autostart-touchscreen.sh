#!/bin/bash
# เปิดเว็บระบบตรวจจับอาหารเต็มจอบน Pi Touchscreen
# ใช้กับ autostart หรือรันมือเมื่อเข้า Desktop

DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# รัน Flask ในพื้นหลัง (ถ้ายังไม่มี process รันอยู่)
if ! pgrep -f "python3 app.py" > /dev/null; then
  source venv/bin/activate 2>/dev/null || true
  python3 app.py &
  sleep 3
fi

# เปิด Chromium เต็มจอ (Kiosk) ไม่มีแถบ URL
BROWSER="chromium-browser"
if command -v chromium &>/dev/null; then
  BROWSER="chromium"
fi

"$BROWSER" --kiosk \
  --noerrdialogs \
  --disable-infobars \
  --no-first-run \
  --disable-session-crashed-bubble \
  http://127.0.0.1:5000
