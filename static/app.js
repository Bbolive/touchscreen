/**
 * ระบบตรวจจับอาหาร - 3 หน้า
 * หน้าแรก: สถานะกล้อง, คำแนะนำ, ปุ่มถ่ายภาพ/ตรวจจับ
 * หน้าที่สอง: ภาพที่ตรวจจับ, น้ำหนัก, ราคา, ชื่ออาหาร, ปุ่มเริ่มใหม่ / ยืนยัน
 * หน้าที่สาม: เสร็จสิ้นการใช้งาน, นับถอยหลัง 5 วินาที กลับหน้าแรก
 */

const API = {
  camera: "/api/camera/status",
  weight: "/api/weight",
  detect: "/api/detect",
};

const COUNTDOWN_SECONDS = 5;

// Elements
const cameraStatusText = document.getElementById("camera-status-text");
const cameraDot = document.getElementById("camera-dot");
const liveWeightEl = document.getElementById("live-weight");
const btnDetect = document.getElementById("btn-detect");
const resultImage = document.getElementById("result-image");
const resultImagePlaceholder = document.getElementById(
  "result-image-placeholder",
);
const resultFoodName = document.getElementById("result-food-name");
const resultWeight = document.getElementById("result-weight");
const resultPrice = document.getElementById("result-price");
const resultNoImageMsg = document.getElementById("result-no-image-msg");
const btnDetectAgain = document.getElementById("btn-detect-again");
const btnConfirm = document.getElementById("btn-confirm");
const countdownNum = document.getElementById("countdown-num");
const btnDoneNow = document.getElementById("btn-done-now");
const inputUpload = document.getElementById("input-upload");
const inputCamera = document.getElementById("input-camera");
const btnUpload = document.getElementById("btn-upload");
const btnCamera = document.getElementById("btn-camera");
const uploadFilename = document.getElementById("upload-filename");

let weightInterval = null;
let countdownTimer = null;

function hasUploadedFile() {
  const fromUpload =
    inputUpload && inputUpload.files && inputUpload.files.length > 0;
  const fromCamera =
    inputCamera && inputCamera.files && inputCamera.files.length > 0;
  return fromUpload || fromCamera;
}

function getSelectedFile() {
  if (inputUpload && inputUpload.files && inputUpload.files.length > 0)
    return inputUpload.files[0];
  if (inputCamera && inputCamera.files && inputCamera.files.length > 0)
    return inputCamera.files[0];
  return null;
}

function updateDetectButtonState() {
  // เปิดให้กดตรวจจับได้เสมอ (ไม่มีกล้อง/ไม่มีรูป ก็ใช้ผลจำลองและ placeholder)
  if (btnDetect) btnDetect.disabled = false;
}

function showScreen(screenId) {
  document
    .querySelectorAll(".screen")
    .forEach((s) => s.classList.remove("active"));
  const el = document.getElementById(screenId);
  if (el) el.classList.add("active");
}

function setCameraStatus(ready, message) {
  cameraStatusText.textContent = message;
  cameraDot.classList.remove("ready", "error");
  cameraDot.classList.add(ready ? "ready" : "error");
  updateDetectButtonState();
}

async function checkCamera() {
  try {
    const res = await fetch(API.camera);
    const data = await res.json();
    setCameraStatus(data.ready, data.message);
  } catch (e) {
    setCameraStatus(false, "ไม่สามารถเชื่อมต่อกล้องได้");
  }
}

async function fetchWeight() {
  try {
    const res = await fetch(API.weight);
    const data = await res.json();
    if (liveWeightEl)
      liveWeightEl.textContent = Number(data.weight_gram).toFixed(1);
  } catch (_) {
    if (liveWeightEl) liveWeightEl.textContent = "--";
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
  const names = ["ข้าวมันไก่", "ผัดกะเพรา", "ก๋วยเตี๋ยว", "ข้าวหมูแดง"];
  const name = names[Math.floor(Math.random() * names.length)];
  const prices = {
    ข้าวมันไก่: 50,
    ผัดกะเพรา: 45,
    ก๋วยเตี๋ยว: 40,
    ข้าวหมูแดง: 50,
  };
  return { label: name, confidence: 0.9, price_per_unit: prices[name] || 45 };
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
      resultNoImageMsg.textContent =
        "ไม่มีภาพจากกล้องหรืออัปโหลด - แสดงผลจำลอง";
      resultNoImageMsg.style.display = "block";
    } else {
      resultNoImageMsg.textContent = "";
      resultNoImageMsg.style.display = "none";
    }
  }

  if (imageBase64) {
    resultImage.src = "data:image/jpeg;base64," + imageBase64;
    resultImage.classList.add("visible");
    resultImagePlaceholder.classList.add("hidden");
  } else {
    resultImage.removeAttribute("src");
    resultImage.classList.remove("visible");
    resultImagePlaceholder.classList.remove("hidden");
  }

  resultFoodName.textContent = detection.label || "ผลจำลอง";
  resultWeight.textContent = Number(weight).toFixed(1) + " กรัม";
  resultPrice.textContent = Number(price).toFixed(0) + " บาท";

  showScreen("screen-result");
}

function clearUpload() {
  if (inputUpload) inputUpload.value = "";
  if (inputCamera) inputCamera.value = "";
  if (uploadFilename) {
    uploadFilename.textContent = "";
    uploadFilename.classList.remove("has-file");
  }
  updateDetectButtonState();
}

function goHome() {
  showScreen("screen-home");
  clearUpload();
  updateDetectButtonState();
  startWeightPolling();
}

function goDone() {
  showScreen("screen-done");
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

  const file = getSelectedFile();
  btnDetect.disabled = true;
  btnDetect.innerHTML = '<span class="btn-icon">⏳</span> กำลังตรวจจับ...';

  try {
    let res;
    if (file) {
      const form = new FormData();
      form.append("image", file);
      res = await fetch(API.detect, { method: "POST", body: form });
    } else {
      res = await fetch(API.detect, { method: "POST" });
    }
    let data = {};
    try {
      data = await res.json();
    } catch (_) {
      data = { detection: getFallbackDetection() };
    }
    if (!res.ok) {
      data.detection = data.detection || getFallbackDetection();
      data.total_price_bath =
        data.total_price_bath ?? data.detection.price_per_unit;
    }
    stopWeightPolling();
    showResultPage(data);
    clearUpload();
  } catch (e) {
    stopWeightPolling();
    showResultPage({
      detection: getFallbackDetection(),
      weight_gram: 0,
      total_price_bath: 45,
    });
    clearUpload();
  }

  btnDetect.innerHTML =
    '<span class="btn-icon">📷</span> ถ่ายภาพ หรือ ตรวจจับอาหาร';
  updateDetectButtonState();
}

function onImageSelected(file) {
  if (uploadFilename && file) {
    uploadFilename.textContent = "ไฟล์ที่เลือก: " + file.name;
    uploadFilename.classList.add("has-file");
    // ไม่ต้อง runDetection ที่นี่
  } else {
    if (uploadFilename) {
      uploadFilename.textContent = "";
      uploadFilename.classList.remove("has-file");
    }
  }
  updateDetectButtonState();
}

if (btnUpload && inputUpload) {
  btnUpload.addEventListener("click", () => inputUpload.click());
  inputUpload.addEventListener("change", () => {
    const file =
      inputUpload.files && inputUpload.files.length > 0
        ? inputUpload.files[0]
        : null;
    if (inputCamera) inputCamera.value = "";
    onImageSelected(file);
  });
}

if (btnCamera && inputCamera) {
  btnCamera.addEventListener("click", () => inputCamera.click());
  inputCamera.addEventListener("change", () => {
    const file =
      inputCamera.files && inputCamera.files.length > 0
        ? inputCamera.files[0]
        : null;
    if (inputUpload) inputUpload.value = "";
    onImageSelected(file);
  });
}

btnDetect.addEventListener("click", () => {
  if (btnDetect.disabled) return;
  if (hasUploadedFile()) {
    runDetection();
  } else {
    if (inputCamera) inputCamera.click();
    else if (inputUpload) inputUpload.click();
  }
});

btnDetectAgain.addEventListener("click", () => {
  goHome();
});

btnConfirm.addEventListener("click", () => {
  goDone();
});

btnConfirm.addEventListener("click", async () => {
  try {
    const payload = {
      label: resultFoodName.textContent,
      price: parseFloat(resultPrice.textContent),
      weight: parseFloat(resultWeight.textContent.replace("กรัม", "")),
      confidence: 0.9,
      start_time: new Date().toISOString(),
    };

    const res = await fetch("/api/confirm", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    console.log("Confirm response:", data);
  } catch (err) {
    console.error("Confirm error:", err);
  }

  goDone();
});

// Init
(async function init() {
  await checkCamera();
  startWeightPolling();
})();
