import tkinter as tk
from tkinter import messagebox
import pyautogui
import pytesseract
import cv2
import threading
import time
from PIL import Image, ImageTk
import re

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class AutoLectureSkipper:
    def __init__(self, master):
        self.master = master
        self.master.title("🎬 Auto Lecture Skipper v1.1")
        self.master.geometry("450x600")
        self.master.configure(bg="#e0f7fa")

        self.click_pos = None
        self.delay_seconds = 0

        # 헤더 라벨
        tk.Label(master, text="🎯 Auto Lecture Skipper", font=("Helvetica", 18, "bold"), bg="#e0f7fa", fg="#006064").pack(pady=15)

        # 버전 정보
        tk.Label(master, text="Version 1.1", font=("Helvetica", 10), bg="#e0f7fa", fg="#0097a7").pack()

        # 위치 설명 텍스트
        self.status_text = tk.Label(master, text="위치 미설정", font=("Helvetica", 11), bg="#e0f7fa", fg="#00796b")
        self.status_text.pack(pady=5)

        # 좌표 설정 버튼
        self.pos_btn = tk.Button(master, text="1️⃣ 재생 버튼 위치 설정", command=self.set_click_position, width=30, height=2, bg="#00796b", fg="white")
        self.pos_btn.pack(pady=10)

        # 시작 버튼
        self.start_btn = tk.Button(master, text="🚀 자동 스킵 시작", command=self.start_process, width=30, height=2, bg="#004d40", fg="white")
        self.start_btn.pack(pady=10)

        # 이미지 라벨
        self.image_label = tk.Label(master, bg="#e0f7fa")
        self.image_label.pack(pady=10)

        # OCR 결과 출력
        self.result_text = tk.Label(master, text="OCR 인식된 시간: 없음", font=("Helvetica", 12), bg="#e0f7fa", fg="#004d40")
        self.result_text.pack(pady=10)

    def set_click_position(self):
        messagebox.showinfo("위치 설정", "재생 버튼 위치를 클릭하세요. 1초 후 마우스 커서 위치를 저장합니다.")
        time.sleep(1)
        self.click_pos = pyautogui.position()
        self.status_text.config(text=f"클릭 위치: {self.click_pos}")
        messagebox.showinfo("성공", f"설정된 위치: {self.click_pos}")

    def start_process(self):
        if not self.click_pos:
            messagebox.showwarning("오류", "먼저 클릭 위치를 설정해주세요!")
            return
        threading.Thread(target=self.capture_and_process).start()

    def capture_and_process(self):
        x, y = self.click_pos
        region = (x, y + 50, 180, 80)
        screenshot = pyautogui.screenshot(region=region)
        screenshot.save("temp_ocr.png")

        img = cv2.imread("temp_ocr.png")
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, None, fx=2, fy=2)
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        text = pytesseract.image_to_string(thresh, lang='kor+eng')

        print("[🔍 OCR 결과]", text)
        self.result_text.config(text=f"OCR 인식된 시간: {text.strip()}")

        match = self.extract_time(text)
        self.update_image(img)

        if match:
            minutes, seconds = map(int, match.split(':'))
            self.delay_seconds = minutes * 60 + seconds
            self.result_text.config(text=f"⏱ {minutes}분 {seconds}초 후 자동 클릭 예정")
            time.sleep(self.delay_seconds)
            pyautogui.click(self.click_pos)
            messagebox.showinfo("완료", f"{self.delay_seconds}초 후 자동 클릭 완료!")
        else:
            messagebox.showerror("실패", "시간 정보를 인식하지 못했습니다.")

    def extract_time(self, text):
        match = re.search(r'(\d{1,2}):(\d{2})', text)
        if match:
            return match.group()
        return None

    def update_image(self, img):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        pil_img = pil_img.resize((180, 80))
        tk_img = ImageTk.PhotoImage(pil_img)
        self.image_label.configure(image=tk_img)
        self.image_label.image = tk_img

if __name__ == '__main__':
    root = tk.Tk()
    app = AutoLectureSkipper(root)
    root.mainloop()
