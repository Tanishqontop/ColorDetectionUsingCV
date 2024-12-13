import tkinter as tk
from tkinter import filedialog, Canvas, Label, Button
from PIL import Image, ImageTk
import cv2
import numpy as np
import threading

class ColorThemeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Color Theme Extraction")
        self.root.geometry("800x600")
        self.root.configure(bg="#f9f9f9")

        # Header
        self.header = Label(
            self.root, text="Extract Color Theme from Image", font=("Helvetica", 20, "bold"),
            bg="#4caf50", fg="white", pady=10
        )
        self.header.pack(fill="x")

        # Drag-and-Drop Area
        self.canvas = Canvas(
            self.root, width=400, height=300, bg="#ffffff", relief="ridge",
            bd=2, highlightthickness=0
        )
        self.canvas.pack(pady=30)
        self.canvas.create_text(
            200, 150, text="Drag and Drop Your File\nor Click to Select",
            font=("Arial", 16), fill="#555555", justify="center"
        )

        # Bind click event to file selection
        self.canvas.bind("<Button-1>", self.open_file_dialog)

        # Color Palette Display
        self.palette_frame = tk.Frame(self.root, bg="#f9f9f9")
        self.palette_frame.pack(pady=10)

        self.palette_label = Label(
            self.palette_frame, text="Extracted Color Palette", font=("Helvetica", 14),
            bg="#f9f9f9", fg="#333"
        )
        self.palette_label.pack(pady=10)

        self.color_display = tk.Frame(self.palette_frame, bg="#f9f9f9")
        self.color_display.pack()

        # Instruction Label
        self.instruction_label = Label(
            self.root, text="Upload an image or start real-time detection.",
            font=("Arial", 12), bg="#f9f9f9", fg="#777"
        )
        self.instruction_label.pack(pady=20)

        # Real-time detection button
        self.realtime_button = Button(
            self.root, text="Start Real-Time Detection", font=("Arial", 12),
            bg="#ff5722", fg="white", relief="flat", command=self.start_realtime_detection
        )
        self.realtime_button.pack(pady=10)

    def open_file_dialog(self, event=None):
        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg;*.png;*.jpeg")]
        )
        if file_path:
            self.display_image(file_path)

    def display_image(self, file_path):
        img = Image.open(file_path)
        img.thumbnail((400, 300))
        self.img_tk = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(200, 150, image=self.img_tk)
        self.extract_colors(file_path)

    def extract_colors(self, file_path):
        # Read the image using OpenCV
        img = cv2.imread(file_path)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Resize image for faster processing
        img = cv2.resize(img, (200, 200))
        img_flat = img.reshape(-1, 3)

        # Use k-means clustering to find dominant colors
        from sklearn.cluster import KMeans
        kmeans = KMeans(n_clusters=5)
        kmeans.fit(img_flat)
        colors = kmeans.cluster_centers_.astype(int)

        # Display extracted colors
        for widget in self.color_display.winfo_children():
            widget.destroy()

        for color in colors:
            hex_color = f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
            frame = tk.Frame(
                self.color_display, bg=hex_color, width=50, height=50, relief="ridge", bd=1
            )
            frame.pack(side="left", padx=5, pady=5)

            # Add color codes below each color swatch
            code_label = tk.Label(
                self.color_display, text=hex_color, font=("Arial", 10), bg="#f9f9f9", fg="#333"
            )
            code_label.pack(side="left", padx=5)

    def start_realtime_detection(self):
        def realtime_color_detection():
            cap = cv2.VideoCapture(0)

            def getColorName(R, G, B):
                # Placeholder color names (customize with a dataset if needed)
                return f"R={R}, G={G}, B={B}"

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                # Resize the frame for display
                frame = cv2.resize(frame, (800, 600))
                
                # Add rectangle to detect color from center of frame
                center_x, center_y = frame.shape[1] // 2, frame.shape[0] // 2
                cv2.rectangle(frame, (center_x - 10, center_y - 10), (center_x + 10, center_y + 10), (255, 255, 255), 2)

                # Get the color inside the rectangle
                b, g, r = frame[center_y, center_x]
                color_name = getColorName(r, g, b)

                # Display the detected color name
                cv2.putText(
                    frame, color_name, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2
                )

                cv2.imshow("Real-Time Color Detection", frame)

                if cv2.waitKey(1) & 0xFF == 27:  # ESC key to exit
                    break

            cap.release()
            cv2.destroyAllWindows()

        threading.Thread(target=realtime_color_detection).start()

# Create Tkinter root
if __name__ == "__main__":
    from sklearn.cluster import KMeans  # Ensure sklearn is installed
    root = tk.Tk()
    app = ColorThemeApp(root)
    root.mainloop()
