import tkinter as tk
from tkinter import messagebox
import pyautogui
import pytesseract
import cv2
import threading
import time
from PIL import Image, ImageTk
import re
import keyboard  # ESC 감지
import winsound  # 효과음 재생

# Tesseract-OCR 경로 설정
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class AutoLectureSkipper:
    def __init__(self, master):
        self.master = master
        self.master.title("🎬 Auto Lecture Skipper v1.1")
        self.master.geometry("450x600")
        self.master.configure(bg="#e0f7fa")

        self.click_pos = None  # 클릭 위치 저장
        self.delay_seconds = 10  # 기본 대기 시간

        # 헤더
        tk.Label(master, text="🎯 Auto Lecture Skipper", font=("Helvetica", 18, "bold"), bg="#e0f7fa", fg="#006064").pack(pady=15)
        tk.Label(master, text="Version 1.3", font=("Helvetica", 10), bg="#e0f7fa", fg="#0097a7").pack()

        # 상태 텍스트
        self.status_text = tk.Label(master, text="위치 미설정", font=("Helvetica", 11), bg="#e0f7fa", fg="#00796b")
        self.status_text.pack(pady=5)

        # 버튼들
        self.pos_btn = tk.Button(master, text="1️⃣ 재생 버튼 위치 설정", command=self.set_click_position, width=30, height=2, bg="#00796b", fg="white")
        self.pos_btn.pack(pady=10)

        self.start_btn = tk.Button(master, text="🚀 자동 스킵 시작", command=self.start_process, width=30, height=2, bg="#004d40", fg="white")
        self.start_btn.pack(pady=10)

        # OCR 이미지 및 결과 표시
        self.image_label = tk.Label(master, bg="#e0f7fa")
        self.image_label.pack(pady=10)

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
        # OCR 루프를 별도 스레드로 실행
        threading.Thread(target=self.capture_and_process_loop).start()

    def capture_and_process_loop(self):
        self.master.configure(bg="#c8e6c9")  # 실행 중: 배경 연두색
        self.status_text.config(text="⏳ 자동 스킵 진행 중", fg="#33691e")

        while True:
            # ESC 누르면 종료
            if keyboard.is_pressed("esc"):
                self.status_text.config(text="⛔ ESC로 중단됨", fg="red")
                self.master.configure(bg="#e0f7fa")
                break

                 # 1. OCR 대상 영역 캡처
            x, y = self.click_pos
            region = (950, 590, 55, 30)
            screenshot = pyautogui.screenshot(region=region)
            screenshot.save("temp_ocr.png")

            # 2. 이미지 전처리
            img = cv2.imread("temp_ocr.png")
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            gray = cv2.resize(gray, None, fx=3, fy=3, interpolation=cv2.INTER_CUBIC)
            gray = cv2.bitwise_not(gray)
            gray = cv2.GaussianBlur(gray, (3, 3), 0)

            thresh = cv2.adaptiveThreshold(
                gray, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11, 2
            )
            # 3. 전처리 이미지 저장 및 결과 표시
            cv2.imwrite("temp_thresh.png", thresh)
            text = pytesseract.image_to_string(thresh, lang='kor+eng')
            print("[🔍 OCR 결과]", text)
            self.result_text.config(text=f"OCR 인식된 시간: {text.strip()}")
            self.update_image(img)

            # 4. 시간 추출 및 처리
            match = self.extract_time(text)
            if match:
                minutes, seconds = map(int, match.split(":"))
                self.delay_seconds = minutes * 60 + seconds
                self.result_text.config(text=f"⏱ {minutes}분 {seconds}초 후 자동 클릭 예정")

                pyautogui.click(self.click_pos)

                # 카운트다운 표시
                for remaining in range(self.delay_seconds, 0, -1):
                    if keyboard.is_pressed("esc"):
                        self.status_text.config(text="⛔ ESC로 중단됨", fg="red")
                        self.master.configure(bg="#e0f7fa")
                        return
                    mins, secs = divmod(remaining, 60)
                    self.result_text.config(text=f"⏱ {mins}분 {secs}초 후 다음 강의")
                    time.sleep(1)
            else:
                self.result_text.config(text="❌ 시간 인식 실패. 프로그램 중단")
                winsound.Beep(1000, 8000)  # 삐 소리 효과음
                self.master.configure(bg="#f8bbd0")  # 분홍색 → 오류 표시
                break

            time.sleep(3)

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

# 프로그램 실행
if __name__ == '__main__':
    root = tk.Tk()
    app = AutoLectureSkipper(root)
    root.mainloop()
