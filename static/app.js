/**
 * ระบบตรวจจับอาหาร - 3 หน้า
 * หน้าแรก: สถานะกล้อง, คำแนะนำ, ปุ่มถ่ายภาพ/ตรวจจับ
 * หน้าที่สอง: ภาพที่ตรวจจับ, น้ำหนัก, ราคา, ชื่ออาหาร, ปุ่มเริ่มใหม่ / ยืนยัน
 * หน้าที่สาม: เสร็จสิ้นการใช้งาน, นับถอยหลัง 5 วินาที กลับหน้าแรก
 */

const API = {
  camera: '/api/camera/status',
  weight: '/api/weight',
  detect: '/api/detect',
};

const COUNTDOWN_SECONDS = 5;

// Elements
const screenHome = document.getElementById('screen-home');
const screenResult = document.getElementById('screen-result');
const screenDone = document.getElementById('screen-done');
const cameraStatusText = document.getElementById('camera-status-text');
const cameraDot = document.getElementById('camera-dot');
const liveWeightEl = document.getElementById('live-weight');
const btnDetect = document.getElementById('btn-detect');
const resultImage = document.getElementById('result-image');
const resultLabelsCanvas = document.getElementById('result-labels-canvas');
const resultImagePlaceholder = document.getElementById('result-image-placeholder');
const resultFoodName = document.getElementById('result-food-name');
const resultWeight = document.getElementById('result-weight');
const resultPrice = document.getElementById('result-price');
const resultNoImageMsg = document.getElementById('result-no-image-msg');
const btnDetectAgain = document.getElementById('btn-detect-again');
const btnConfirm = document.getElementById('btn-confirm');
const countdownNum = document.getElementById('countdown-num');
const btnDoneNow = document.getElementById('btn-done-now');
const inputUpload = document.getElementById('input-upload');
const btnUpload = document.getElementById('btn-upload');
const uploadFilename = document.getElementById('upload-filename');

let weightInterval = null;
let countdownTimer = null;

function hasUploadedFile() {
  return inputUpload && inputUpload.files && inputUpload.files.length > 0;
}

function updateDetectButtonState() {
  // เปิดให้กดตรวจจับได้เสมอ (ไม่มีกล้อง/ไม่มีรูป ก็ใช้ผลจำลองและ placeholder)
  if (btnDetect) btnDetect.disabled = false;
}

function showScreen(screenId) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  const el = document.getElementById(screenId);
  if (el) el.classList.add('active');
}

function setCameraStatus(ready, message) {
  cameraStatusText.textContent = message;
  cameraDot.classList.remove('ready', 'error');
  cameraDot.classList.add(ready ? 'ready' : 'error');
  updateDetectButtonState();
}

async function checkCamera() {
  try {
    const res = await fetch(API.camera);
    const data = await res.json();
    setCameraStatus(data.ready, data.message);
  } catch (e) {
    setCameraStatus(false, 'ไม่สามารถเชื่อมต่อกล้องได้');
  }
}

async function fetchWeight() {
  try {
    const res = await fetch(API.weight);
    const data = await res.json();
    if (liveWeightEl) liveWeightEl.textContent = Number(data.weight_gram).toFixed(1);
  } catch (_) {
    if (liveWeightEl) liveWeightEl.textContent = '--';
  }
}

function startWeightPolling() {
  fetchWeight();
  weightInterval = setInterval(fetchWeight, 1500);
}

function stopWeightPolling() {
  if (weightInterval) {
    clearInterval(weightInterval);
    weightInterval = null;
  }
}

/** ผลจำลองเมื่อไม่มี detection จาก server (ไม่มีภาพหรือ error) */
function getFallbackDetection() {
  const names = ['ข้าวมันไก่', 'ผัดกะเพรา', 'ก๋วยเตี๋ยว', 'ข้าวหมูแดง'];
  const name = names[Math.floor(Math.random() * names.length)];
  const prices = { 'ข้าวมันไก่': 50, 'ผัดกะเพรา': 45, 'ก๋วยเตี๋ยว': 40, 'ข้าวหมูแดง': 50 };
  return { label: name, confidence: 0.9, price_per_unit: prices[name] || 45 };
}

/** วาด label บน canvas ตาม detections (พิกัด box เทียบภาพ) — ใช้บนมือถือเมื่อเซิร์ฟเวอร์วาดไม่ได้ */
function drawLabelsOnCanvas(detections, img, canvas) {
  if (!canvas || !img || !detections || !Array.isArray(detections) || detections.length === 0) {
    if (canvas) {
      const ctx = canvas.getContext('2d');
      if (ctx) ctx.clearRect(0, 0, canvas.width, canvas.height);
    }
    return;
  }
  const nw = img.naturalWidth;
  const nh = img.naturalHeight;
  if (!nw || !nh) return;
  const rect = img.getBoundingClientRect();
  const dw = Math.round(rect.width);
  const dh = Math.round(rect.height);
  if (dw <= 0 || dh <= 0) return;
  canvas.width = dw;
  canvas.height = dh;
  canvas.style.width = rect.width + 'px';
  canvas.style.height = rect.height + 'px';
  const ctx = canvas.getContext('2d');
  if (!ctx) return;
  ctx.clearRect(0, 0, dw, dh);
  // รองรับ object-fit: cover — ภาพ scale ให้ cover พื้นที่ แล้ว center
  const scale = Math.max(dw / nw, dh / nh);
  const offsetX = (dw - nw * scale) / 2;
  const offsetY = (dh - nh * scale) / 2;
  const fontPx = Math.max(12, Math.min(18, dw / 18));
  ctx.font = `600 ${fontPx}px "Sarabun", sans-serif`;
  ctx.textBaseline = 'top';
  for (const d of detections) {
    const box = d.box;
    if (!box || box.length < 4) continue;
    const x1 = box[0] * scale + offsetX;
    const y1 = box[1] * scale + offsetY;
    const x2 = box[2] * scale + offsetX;
    const y2 = box[3] * scale + offsetY;
    const w = x2 - x1;
    const h = y2 - y1;
    const label = (d.label_th || d.label || '').trim() || '?';
    ctx.strokeStyle = 'rgba(0,180,80,0.9)';
    ctx.lineWidth = 2;
    ctx.strokeRect(x1, y1, w, h);
    ctx.fillStyle = 'rgba(0,180,80,0.85)';
    const pad = 2;
    const tw = ctx.measureText(label).width;
    const th = fontPx + 4;
    ctx.fillRect(x1, y1 - th - pad, tw + 6, th + pad);
    ctx.fillStyle = '#fff';
    ctx.fillText(label, x1 + 3, y1 - th - pad + 2);
  }
}

function showResultPage(data) {
  let detection = data.detection;
  const noImage = data.no_image === true;
  if (!detection || !detection.label) {
    detection = getFallbackDetection();
  }
  const weight = data.weight_gram ?? 0;
  const price = data.total_price_bath ?? detection.price_per_unit ?? 0;
  const imageBase64 = data.image_base64;

  if (resultNoImageMsg) {
    if (noImage || !imageBase64) {
      resultNoImageMsg.textContent = 'ไม่มีภาพจากกล้องหรืออัปโหลด - แสดงผลจำลอง';
      resultNoImageMsg.style.display = 'block';
    } else {
      resultNoImageMsg.textContent = '';
      resultNoImageMsg.style.display = 'none';
    }
  }

  const detections = data.detections && Array.isArray(data.detections) ? data.detections : [];

  if (imageBase64) {
    resultImage.src = 'data:image/jpeg;base64,' + imageBase64;
    resultImage.classList.add('visible');
    resultImagePlaceholder.classList.add('hidden');
    function drawWhenReady() {
      drawLabelsOnCanvas(detections, resultImage, resultLabelsCanvas);
    }
    if (resultImage.complete) {
      drawWhenReady();
    } else {
      resultImage.onload = drawWhenReady;
    }
  } else {
    resultImage.removeAttribute('src');
    resultImage.classList.remove('visible');
    resultImagePlaceholder.classList.remove('hidden');
    drawLabelsOnCanvas([], resultImage, resultLabelsCanvas);
  }

  resultFoodName.textContent = detection.label || 'ผลจำลอง';
  resultWeight.textContent = Number(weight).toFixed(1) + ' กรัม';
  resultPrice.textContent = Number(price).toFixed(0) + ' บาท';

  showScreen('screen-result');
}

function clearUpload() {
  if (inputUpload) {
    inputUpload.value = '';
    if (uploadFilename) {
      uploadFilename.textContent = '';
      uploadFilename.classList.remove('has-file');
    }
  }
  updateDetectButtonState();
}

function goHome() {
  showScreen('screen-home');
  clearUpload();
  updateDetectButtonState();
  startWeightPolling();
}

function goDone() {
  showScreen('screen-done');
  stopWeightPolling();
  let sec = COUNTDOWN_SECONDS;
  countdownNum.textContent = sec;

  if (countdownTimer) clearInterval(countdownTimer);
  countdownTimer = setInterval(() => {
    sec -= 1;
    countdownNum.textContent = sec;
    if (sec <= 0) {
      clearInterval(countdownTimer);
      countdownTimer = null;
      goHome();
    }
  }, 1000);
}

async function runDetection() {
  if (btnDetect.disabled) return;

  const useUpload = hasUploadedFile();
  btnDetect.disabled = true;
  btnDetect.innerHTML = '<span class="btn-icon">⏳</span> กำลังตรวจจับ...';

  try {
    let res;
    if (useUpload && inputUpload.files[0]) {
      const form = new FormData();
      form.append('image', inputUpload.files[0]);
      res = await fetch(API.detect, { method: 'POST', body: form });
    } else {
      res = await fetch(API.detect, { method: 'POST' });
    }
    let data = {};
    try {
      data = await res.json();
    } catch (_) {
      data = { detection: getFallbackDetection() };
    }
    if (!res.ok) {
      data.detection = data.detection || getFallbackDetection();
      data.total_price_bath = data.total_price_bath ?? data.detection.price_per_unit;
    }
    stopWeightPolling();
    showResultPage(data);
    clearUpload();
  } catch (e) {
    stopWeightPolling();
    showResultPage({ detection: getFallbackDetection(), weight_gram: 0, total_price_bath: 45 });
    clearUpload();
  }

  btnDetect.innerHTML = '<span class="btn-icon">📷</span> ถ่ายภาพ หรือ ตรวจจับอาหาร';
  updateDetectButtonState();
}

// Event listeners
if (btnUpload && inputUpload) {
  btnUpload.addEventListener('click', () => inputUpload.click());
  inputUpload.addEventListener('change', () => {
    if (uploadFilename) {
      if (inputUpload.files.length > 0) {
        uploadFilename.textContent = inputUpload.files[0].name;
        uploadFilename.classList.add('has-file');
      } else {
        uploadFilename.textContent = '';
        uploadFilename.classList.remove('has-file');
      }
    }
    updateDetectButtonState();
  });
}

btnDetect.addEventListener('click', () => {
  if (!btnDetect.disabled) runDetection();
});

btnDetectAgain.addEventListener('click', () => {
  goHome();
});

btnConfirm.addEventListener('click', () => {
  goDone();
});

btnDoneNow.addEventListener('click', () => {
  if (countdownTimer) {
    clearInterval(countdownTimer);
    countdownTimer = null;
  }
  goHome();
});

// Init
(async function init() {
  await checkCamera();
  startWeightPolling();
})();
