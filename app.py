import tkinter as tk
from tkinter import simpledialog, messagebox
import cv2
import os
import face_recognition
import pandas as pd
from datetime import datetime

# Paths
PHOTO_FOLDER = "photos"
ATTENDANCE_FILE = "attendance.csv"

# Ensure directories and files exist
os.makedirs(PHOTO_FOLDER, exist_ok=True)
if not os.path.exists(ATTENDANCE_FILE):
    pd.DataFrame(columns=["Roll No", "Name", "Date", "Time"]).to_csv(ATTENDANCE_FILE, index=False)

# Functions
def capture_photo(filename):
    """Captures a photo and saves it with the given filename."""
    cam = cv2.VideoCapture(0)
    cv2.namedWindow("Capture Photo")

    while True:
        ret, frame = cam.read()
        if not ret:
            print("Failed to grab frame")
            break
        cv2.imshow("Capture Photo", frame)

        key = cv2.waitKey(1)
        if key % 256 == 32:  # Space bar to capture
            cv2.imwrite(filename, frame)
            print(f"Photo saved as {filename}")
            break

    cam.release()
    cv2.destroyAllWindows()

def register_student():
    """Registers a new student."""
    roll_no = simpledialog.askstring("Input", "Enter Roll Number:")
    name = simpledialog.askstring("Input", "Enter Name:")

    if not roll_no or not name:
        messagebox.showerror("Error", "Roll number and name are required!")
        return

    photo_path = os.path.join(PHOTO_FOLDER, f"{roll_no}_{name}.png")
    messagebox.showinfo("Info", "Press space bar to capture photo.")
    capture_photo(photo_path)
    messagebox.showinfo("Success", f"Student {name} registered successfully!")

def mark_attendance():
    """Marks attendance by verifying the student."""
    roll_no = simpledialog.askstring("Input", "Enter Roll Number:")

    if not roll_no:
        messagebox.showerror("Error", "Roll number is required!")
        return

    # Capture the current photo
    temp_photo = "temp_photo.png"
    messagebox.showinfo("Info", "Press space bar to capture photo.")
    capture_photo(temp_photo)

    # Match the photo
    for file in os.listdir(PHOTO_FOLDER):
        if file.startswith(roll_no + "_"):
            saved_photo_path = os.path.join(PHOTO_FOLDER, file)
            saved_image = face_recognition.load_image_file(saved_photo_path)
            saved_encoding = face_recognition.face_encodings(saved_image)[0]

            temp_image = face_recognition.load_image_file(temp_photo)
            temp_encodings = face_recognition.face_encodings(temp_image)

            if temp_encodings and face_recognition.compare_faces([saved_encoding], temp_encodings[0])[0]:
                name = file.split("_")[1].replace(".png", "")
                log_attendance(roll_no, name)
                os.remove(temp_photo)
                messagebox.showinfo("Success", "Attendance marked successfully!")
                return

    os.remove(temp_photo)
    messagebox.showerror("Error", "Face not recognized!")

def log_attendance(roll_no, name):
    """Logs attendance to the CSV file."""
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%H:%M:%S")

    # Read the existing CSV file
    df = pd.read_csv(ATTENDANCE_FILE)
    
    # Check for duplicate entries
    if not ((df["Roll No"] == roll_no) & (df["Date"] == date)).any():
        # Create a new row as a dictionary
        new_entry = {"Roll No": roll_no, "Name": name, "Date": date, "Time": time}

        # Add the new row to the DataFrame
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

        # Save the updated DataFrame to the CSV file
        df.to_csv(ATTENDANCE_FILE, index=False)


# GUI Setup
root = tk.Tk()
root.title("Facial Recognition Attendance System")
root.geometry("400x200")

tk.Label(root, text="Attendance System", font=("Arial", 18)).pack(pady=10)

tk.Button(root, text="Register", command=register_student, width=20, height=2).pack(pady=5)
tk.Button(root, text="Mark Attendance", command=mark_attendance, width=20, height=2).pack(pady=5)

root.mainloop()