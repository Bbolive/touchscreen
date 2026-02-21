# -*- coding: utf-8 -*-
"""
การตั้งค่าโมเดลและราคาอาหารสำหรับระบบตรวจจับอาหาร
"""
import os

# path โมเดล YOLOv8 (best.pt) - แก้เป็น path จริงที่เก็บไฟล์
MODEL_PATH = os.environ.get(
    'FOOD_MODEL_PATH',
    r'c:\Users\ssoms\Downloads\AI Food Recognition System Project\best.pt'
)

# ชื่อคลาสจาก data.yaml ของโปรเจกต์ (18 คลาส)
CLASS_NAMES = [
    'boiled_chicken', 'boiled_chicken_blood_jelly', 'boiled_egg',
    'chainese_sausage', 'chicken_drumstick', 'chicken_rice', 'chicken_shredded',
    'crispy_pork', 'cucumber', 'daikon_radish', 'fried_chicken', 'fried_tofo',
    'minced_pork', 'noodle', 'red_pork', 'red_pork_and_crispy_pork',
    'rice', 'stir_fried_basil'
]

# ชื่อแสดงภาษาไทย (ถ้ามี)
CLASS_NAMES_TH = {
    'boiled_chicken': 'ไก่ต้ม',
    'boiled_chicken_blood_jelly': 'เลือดไก่',
    'boiled_egg': 'ไข่ต้ม',
    'chainese_sausage': 'ไส้กรอก',
    'chicken_drumstick': 'น่องไก่',
    'chicken_rice': 'ข้าวมันไก่',
    'chicken_shredded': 'ไก่ฉีก',
    'crispy_pork': 'หมูกรอบ',
    'cucumber': 'แตงกวา',
    'daikon_radish': 'หัวไชเท้า',
    'fried_chicken': 'ไก่ทอด',
    'fried_tofo': 'เต้าหู้ทอด',
    'minced_pork': 'หมูสับ',
    'noodle': 'ก๋วยเตี๋ยว',
    'red_pork': 'หมูแดง',
    'red_pork_and_crispy_pork': 'หมูแดงกับหมูกรอบ',
    'rice': 'ข้าว',
    'stir_fried_basil': 'ผัดกะเพรา',
}

# ราคาต่อหน่วย (บาท) ตามคลาส - แก้ได้ตามเมนูจริง
PRICE_PER_CLASS = {
    'boiled_chicken': 25,
    'boiled_chicken_blood_jelly': 20,
    'boiled_egg': 10,
    'chainese_sausage': 15,
    'chicken_drumstick': 30,
    'chicken_rice': 45,
    'chicken_shredded': 25,
    'crispy_pork': 40,
    'cucumber': 5,
    'daikon_radish': 5,
    'fried_chicken': 35,
    'fried_tofo': 15,
    'minced_pork': 25,
    'noodle': 40,
    'red_pork': 45,
    'red_pork_and_crispy_pork': 50,
    'rice': 10,
    'stir_fried_basil': 45,
}

# ความมั่นใจขั้นต่ำ (ถ้าต่ำกว่านี้ไม่นับ)
CONFIDENCE_THRESHOLD = 0.25

# --- วัตถุดิบ (จาก Roboflow) → ชื่อเมนู (สำหรับแสดงบนเว็บ) ---
# ใช้สำหรับแมปผลตรวจจับวัตถุดิบเป็นชื่ออาหาร/เมนู
INGREDIENT_TO_MENU = {
    # ข้าวมันไก่ทอด
    "fried_chicken": "ข้าวมันไก่ทอด",
    "cucumber": "ข้าวมันไก่ทอด",
    "boiled_chicken_blood_jelly": "ข้าวมันไก่ทอด",
    "rice": "ข้าวมันไก่ทอด",
    # ข้าวมันไก่ต้ม
    "boiled_chicken": "ข้าวมันไก่ต้ม",
    # "boiled_chicken_blood_jelly": "ข้าวมันไก่ต้ม",  # ซ้ำกับด้านบน
    # "cucumber": "ข้าวมันไก่ต้ม",
    # "rice": "ข้าวมันไก่ต้ม",
    # ก๋วยเตี๋ยวไก่น่อง
    "chicken_drumstick": "ก๋วยเตี๋ยวไก่น่อง",
    "noodle": "ก๋วยเตี๋ยวไก่น่อง",
    "daikon_radish": "ก๋วยเตี๋ยวไก่น่อง",
    # ก๋วยเตี๋ยวไก่ฉีก
    "chicken_shredded": "ก๋วยเตี๋ยวไก่ฉีก",
    # "noodle": "ก๋วยเตี๋ยวไก่ฉีก",
    # "daikon_radish": "ก๋วยเตี๋ยวไก่ฉีก",
    # ข้าวหมูแดง
    "boiled_egg": "ข้าวหมูแดง",
    "red_pork": "ข้าวหมูแดง",
    "chainese_sausage": "ข้าวหมูแดง",  # สะกดตามชื่อในโมเดล
    # "cucumber": "ข้าวหมูแดง",
    # "rice": "ข้าวหมูแดง",
    # ข้าวหมูกรอบ
    "crispy_pork": "ข้าวหมูกรอบ",
    # "boiled_egg": "ข้าวหมูกรอบ",
    # "cucumber": "ข้าวหมูกรอบ",
    # "chainese_sausage": "ข้าวหมูกรอบ",
    # "rice": "ข้าวหมูกรอบ",
    # ข้าวหมูแดงและข้าวหมูกรอบ
    "red_pork_and_crispy_pork": "ข้าวหมูแดงและข้าวหมูกรอบ",
    # ข้าวกะเพราหมูสับเต้าหู้ทอด (ในโมเดลเป็น stir_fried_basil)
    "fried_tofo": "ข้าวกะเพราหมูสับเต้าหู้ทอด",
    "stir_fried_basil": "ข้าวกะเพราหมูสับเต้าหู้ทอด",
    "minced_pork": "ข้าวกะเพราหมูสับเต้าหู้ทอด",
    # "rice": "ข้าวกะเพราหมูสับเต้าหู้ทอด",
}

# ชุดวัตถุดิบของแต่ละเมนู (ใช้สำหรับจับคู่จากผลตรวจจับ → เลือกเมนู)
# เรียงจากเมนูที่เฉพาะเจาะจงมาก (วัตถุดิบมาก) ไปน้อย เพื่อให้เลือกเมนูที่ตรงที่สุดก่อน
MENU_DEFINITIONS = [
    {"name": "ข้าวหมูแดงและข้าวหมูกรอบ", "ingredients": {"boiled_egg", "red_pork", "crispy_pork", "cucumber", "chainese_sausage", "red_pork_and_crispy_pork", "rice"}, "price": 55},
    {"name": "ข้าวมันไก่ทอด", "ingredients": {"fried_chicken", "cucumber", "boiled_chicken_blood_jelly", "rice"}, "price": 50},
    {"name": "ข้าวมันไก่ต้ม", "ingredients": {"boiled_chicken", "boiled_chicken_blood_jelly", "cucumber", "rice"}, "price": 45},
    {"name": "ก๋วยเตี๋ยวไก่น่อง", "ingredients": {"chicken_drumstick", "noodle", "daikon_radish"}, "price": 50},
    {"name": "ก๋วยเตี๋ยวไก่ฉีก", "ingredients": {"chicken_shredded", "noodle", "daikon_radish"}, "price": 45},
    {"name": "ข้าวหมูแดง", "ingredients": {"boiled_egg", "red_pork", "cucumber", "chainese_sausage", "rice"}, "price": 50},
    {"name": "ข้าวหมูกรอบ", "ingredients": {"boiled_egg", "crispy_pork", "cucumber", "chainese_sausage", "rice"}, "price": 50},
    {"name": "ข้าวกะเพราหมูสับเต้าหู้ทอด", "ingredients": {"fried_tofo", "rice", "stir_fried_basil", "minced_pork"}, "price": 45},
]

# เมนูที่ไม่มีใน MENU_DEFINITIONS จะใช้ราคาจาก PRICE_PER_CLASS รวม (หรือ fallback)


def ingredients_to_menu(detected_ingredient_labels):
    """
    แปลงชุดวัตถุดิบที่ตรวจจับได้ (list/set ของชื่อคลาส เช่น rice, fried_chicken)
    เป็นชื่อเมนูและราคาที่เหมาะสม
    ใช้หลัก "ความตรงกันมากที่สุด" ถ้าตรวจจับได้ไม่ครบทุกอย่างก็ยังเลือกเมนูที่ใกล้เคียงที่สุด
    Returns:
        (menu_name, price) หรือ (None, None) ถ้าไม่มีเมนูที่ตรง
    """
    if not detected_ingredient_labels:
        return None, None
    detected_set = set(detected_ingredient_labels)

    # วิธีที่ 1: ถ้ามีเมนูที่วัตถุดิบครบเป็น subset ของที่ตรวจจับได้ → ใช้เมนูนั้น (เฉพาะเจาะจงที่สุด)
    best = None
    best_len = 0
    for m in MENU_DEFINITIONS:
        ing = m["ingredients"]
        if ing <= detected_set and len(ing) > best_len:
            best = m
            best_len = len(ing)
    if best:
        return best["name"], best["price"]

    # วิธีที่ 2: เลือกเมนูที่ "ตรงกับวัตถุดิบที่ตรวจจับได้มากที่สุด" (อย่างน้อย 2 อย่าง)
    best = None
    best_score = 0
    for m in MENU_DEFINITIONS:
        ing = m["ingredients"]
        overlap = len(detected_set & ing)
        if overlap >= 2 and overlap > best_score:
            best = m
            best_score = overlap
    if best:
        return best["name"], best["price"]

    # วิธีที่ 3: ตรงแค่ 1 อย่าง ก็ใช้ INGREDIENT_TO_MENU แมปวัตถุดิบหลักเป็นเมนู
    for label in detected_ingredient_labels:
        menu_name = INGREDIENT_TO_MENU.get(label)
        if menu_name:
            for m in MENU_DEFINITIONS:
                if m["name"] == menu_name:
                    return m["name"], m["price"]
    return None, None
