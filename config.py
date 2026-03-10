# -*- coding: utf-8 -*-
"การตั้งค่าโมเดลและราคาอาหารสำหรับระบบตรวจจับอาหารอัตโนมัติ"

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "models", "best.pt")
if not os.path.exists(MODEL_PATH):
    raise FileNotFoundError(f"Model not found: {MODEL_PATH}")

# ชื่อคลาสจาก data.yaml ของโปรเจกต์ (18 คลาส)
CLASS_NAMES = [
    "boiled_chicken",
    "boiled_chicken_blood_jelly",
    "boiled_egg",
    "chainese_sausage",
    "chicken_drumstick",
    "chicken_rice",
    "chicken_shredded",
    "crispy_pork",
    "cucumber",
    "daikon_radish",
    "fried_chicken",
    "fried_tofo",
    "minced_pork",
    "noodle",
    "red_pork",
    "red_pork_and_crispy_pork",
    "rice",
    "stir_fried_basil",
]

# ชื่อแสดงภาษาไทย (ถ้ามี)
CLASS_NAMES_TH = {
    "boiled_chicken": "ไก่ต้ม",
    "boiled_chicken_blood_jelly": "เลือดไก่",
    "boiled_egg": "ไข่ต้ม",
    "chainese_sausage": "กุนเชียง",
    "chicken_drumstick": "น่องไก่",
    "chicken_rice": "ข้าวมันไก่",
    "chicken_shredded": "ไก่ฉีก",
    "crispy_pork": "หมูกรอบ",
    "cucumber": "แตงกวา",
    "daikon_radish": "หัวไชเท้า",
    "fried_chicken": "ไก่ทอด",
    "fried_tofo": "เต้าหู้ทอด",
    "minced_pork": "หมูสับ",
    "noodle": "ก๋วยเตี๋ยว",
    "red_pork": "หมูแดง",
    "red_pork_and_crispy_pork": "หมูแดงกับหมูกรอบ",
    "rice": "ข้าว",
    "stir_fried_basil": "ผัดกะเพรา",
}


def label_to_th(label):
    return CLASS_NAMES_TH.get(label, label)


# ราคาต่อหน่วย (บาท) ตามคลาส - แก้ได้ตามเมนูจริง
PRICE_PER_CLASS = {
    "boiled_chicken": 25,
    "boiled_chicken_blood_jelly": 20,
    "boiled_egg": 10,
    "chainese_sausage": 15,
    "chicken_drumstick": 30,
    "chicken_rice": 45,
    "chicken_shredded": 25,
    "crispy_pork": 40,
    "cucumber": 5,
    "daikon_radish": 5,
    "fried_chicken": 35,
    "fried_tofo": 15,
    "minced_pork": 25,
    "noodle": 40,
    "red_pork": 45,
    "red_pork_and_crispy_pork": 50,
    "rice": 10,
    "stir_fried_basil": 45,
}

# ความมั่นใจขั้นต่ำ (ถ้าต่ำกว่านี้ไม่นับ)
CONFIDENCE_THRESHOLD = 0.35

MENU_DEFINITIONS = [
    {
        "name": "ข้าวมันไก่ทอด",
        "ingredients": {
            "fried_chicken",
            "cucumber",
            "boiled_chicken_blood_jelly",
            "rice",
        },
        "key": {"fried_chicken"},
        "price": 50,
    },
    {
        "name": "ข้าวมันไก่ต้ม",
        "ingredients": {
            "boiled_chicken",
            "boiled_chicken_blood_jelly",
            "cucumber",
            "rice",
            "chicken_rice",
        },
        "key": {"boiled_chicken", "chicken_rice"},
        "price": 45,
    },
    {
        "name": "ข้าวมันไก่ทอดไก่ต้ม",
        "ingredients": {
            "fried_chicken",
            "boiled_chicken",
            "boiled_chicken_blood_jelly",
            "cucumber",
            "rice",
            "chicken_rice",
        },
        "key": {"fried_chicken", "boiled_chicken"},
        "price": 55,
    },
    {
        "name": "ก๋วยเตี๋ยวไก่น่อง",
        "ingredients": {"chicken_drumstick", "noodle", "daikon_radish"},
        "key": {"chicken_drumstick", "noodle"},
        "price": 50,
    },
    {
        "name": "ก๋วยเตี๋ยวไก่ฉีก",
        "ingredients": {"chicken_shredded", "noodle", "daikon_radish"},
        "key": {"chicken_shredded", "noodle"},
        "price": 45,
    },
    {
        "name": "ข้าวหมูแดง",
        "ingredients": {
            "boiled_egg",
            "red_pork",
            "cucumber",
            "chainese_sausage",
            "rice",
        },
        "key": {"red_pork"},
        "price": 50,
    },
    {
        "name": "ข้าวหมูกรอบ",
        "ingredients": {
            "boiled_egg",
            "crispy_pork",
            "cucumber",
            "chainese_sausage",
            "rice",
        },
        "key": {"crispy_pork"},
        "price": 50,
    },
    {
        "name": "ข้าวหมูแดงและข้าวหมูกรอบ",
        "ingredients": {
            "boiled_egg",
            "red_pork",
            "crispy_pork",
            "cucumber",
            "chainese_sausage",
            "rice",
        },
        "key": {"red_pork", "crispy_pork"},
        "price": 55,
    },
    {
        "name": "ข้าวกะเพราหมูสับเต้าหู้ทอด",
        "ingredients": {"fried_tofo", "rice", "stir_fried_basil", "minced_pork"},
        "key": {"stir_fried_basil"},
        "price": 45,
    },
]

# เมนูที่ไม่มีใน MENU_DEFINITIONS จะใช้ราคาจาก PRICE_PER_CLASS รวม (หรือ fallback)


def ingredients_to_menu(detected_items):
    if not detected_items:
        return None, None

    # 1️⃣ กรอง confidence ต่ำ
    detected = {
        item["label"]: item["confidence"]
        for item in detected_items
        if item["confidence"] >= CONFIDENCE_THRESHOLD
    }

    if not detected:
        return None, None

    detected_set = set(detected.keys())
    print("DETECTED:", detected_set)

    # =====================================================
    # 🔥 PRIORITY ORDER (สำคัญมาก)
    # =====================================================

    # ===== 1️⃣ ข้าวกะเพรา (เฉพาะทางสุด) =====
    if "stir_fried_basil" in detected_set:
        if "minced_pork" in detected_set and "fried_tofo" in detected_set:
            return "ข้าวกะเพราหมูสับเต้าหู้ทอด", 45
        return "ข้าวกะเพราหมูสับเต้าหู้ทอด", 45

# ===== 2️⃣ ก๋วยเตี๋ยว =====
    if "noodle" in detected_set and "rice" not in detected_set:
        if "chicken_drumstick" in detected_set:
            return "ก๋วยเตี๋ยวไก่น่อง", 50
        if "chicken_shredded" in detected_set:
            return "ก๋วยเตี๋ยวไก่ฉีก", 45
        return "ก๋วยเตี๋ยวไก่ฉีก", 45

    # ===== 3️⃣ ข้าวหมูแดง / หมูกรอบ =====
    if "rice" in detected_set:
        if "red_pork" in detected_set and "crispy_pork" in detected_set:
            return "ข้าวหมูแดงและข้าวหมูกรอบ", 55
        if "red_pork" in detected_set:
            return "ข้าวหมูแดง", 50
        if "crispy_pork" in detected_set:
            return "ข้าวหมูกรอบ", 50

    # ===== 4️⃣ ข้าวมันไก่ =====
    has_rice = "rice" in detected_set or "chicken_rice" in detected_set
    has_fried = "fried_chicken" in detected_set
    has_boiled = "boiled_chicken" in detected_set or "chicken_shredded" in detected_set
    has_blood = "boiled_chicken_blood_jelly" in detected_set
    has_cucumber = "cucumber" in detected_set

    if has_rice:
        if has_fried and has_boiled:
            return "ข้าวมันไก่ทอดผสม", 55
        if has_fried:
            return "ข้าวมันไก่ทอด", 50
        if has_boiled:
            return "ข้าวมันไก่ต้ม", 45
        if has_blood or has_cucumber:
            return "ข้าวมันไก่", 45

    # =====================================================
    # 🤖 AI SCORING SYSTEM (fallback อัจฉริยะ)
    # =====================================================

    best_menu = None
    best_score = 0

    for menu in MENU_DEFINITIONS:

        menu_ingredients = menu["ingredients"]
        key_ingredients = menu.get("key", set())

        if key_ingredients and not (key_ingredients & detected_set):
            continue

        matched = menu_ingredients & detected_set
        if not matched:
            continue

        matched_conf_score = sum(detected[i] for i in matched)
        coverage = len(matched) / len(menu_ingredients)

        extra = detected_set - menu_ingredients
        penalty = len(extra) * 0.08

        final_score = (matched_conf_score * 0.6) + (coverage * 0.4) - penalty

        if final_score > best_score:
            best_score = final_score
            best_menu = menu

    if best_menu and best_score >= 0.35:
        return best_menu["name"], best_menu["price"]

    # ===== fallback คิดตามวัตถุดิบ =====
    total_price = sum(PRICE_PER_CLASS.get(label, 0) for label in detected_set)

    if total_price > 0:
        return "ไม่ทราบเมนู (คิดตามวัตถุดิบ)", total_price

    return None, None
