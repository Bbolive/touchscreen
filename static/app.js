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
const resultImagePlaceholder = document.getElementById('result-image-placeholder');
const resultFoodName = document.getElementById('result-food-name');
const resultWeight = document.getElementById('result-weight');
const resultPrice = document.getElementById('result-price');
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
  const ready = cameraDot && cameraDot.classList.contains('ready');
  const hasFile = hasUploadedFile();
  btnDetect.disabled = !ready && !hasFile;
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

function showResultPage(data) {
  const detection = data.detection || {};
  const weight = data.weight_gram ?? 0;
  const price = data.total_price_bath ?? 0;
  const imageBase64 = data.image_base64;

  if (imageBase64) {
    resultImage.src = 'data:image/jpeg;base64,' + imageBase64;
    resultImage.classList.add('visible');
    resultImagePlaceholder.classList.add('hidden');
  } else {
    resultImage.removeAttribute('src');
    resultImage.classList.remove('visible');
    resultImagePlaceholder.classList.remove('hidden');
  }

  resultFoodName.textContent = detection.label || '-';
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
    const data = await res.json();
    stopWeightPolling();
    showResultPage(data);
    clearUpload();
  } catch (e) {
    btnDetect.innerHTML = '<span class="btn-icon">📷</span> ถ่ายภาพ หรือ ตรวจจับอาหาร';
    updateDetectButtonState();
    return;
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
