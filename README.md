# Vision Mouse Control

> Real-time hand gesture mouse control using Python, OpenCV, and MediaPipe.

Control your system cursor using hand movements detected through your webcam. This project demonstrates real-time computer vision, gesture recognition, and human-computer interaction using pure Python.

---

## Features

- **Real-time Detection:** 21-point hand landmark detection.
- **Cursor Control:** Smooth movement using the index finger.
- **Gesture Actions:** Pinch to click or hold.
- **Jitter Reduction:** Interpolation for stable cursor movement.
- **Webcam Support:** Plug-and-play with standard cameras.

---

## How It Works

1.  **Capture:** Video frames are grabbed via OpenCV.
2.  **Detect:** MediaPipe identifies hand landmarks.
3.  **Extract:** Fingertip coordinates are isolated.
4.  **Map:** Camera coordinates are converted to screen resolution.
5.  **Calculate:** Distance between thumb and index finger determines clicks.
6.  **Action:** PyAutoGUI triggers mouse events.

---

## Project Structure

```text
vision-mouse-control/
│
├── hand_mouse_mvp.py      # Main application entry point
├── requirements.txt       # Project dependencies
│
└── docs/                  # Documentation
    ├── prd.md
    ├── tech_stack.md
    ├── app_flow.md
    └── implementation_plan.md

## Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/vision-mouse-control.git](https://github.com/your-username/vision-mouse-control.git)
    cd vision-mouse-control
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

---

## Usage

1.  **Run the application:**
    ```bash
    python hand_mouse_mvp.py
    ```

2.  **Controls:**
    * Move hand to move cursor.
    * Pinch thumb and index finger to click.
    * Press `Q` to exit the application.

---

## Tech Stack

* **Python 3.x**
* **OpenCV** (Computer Vision)
* **MediaPipe** (Hand Tracking)
* **PyAutoGUI** (Interface Control)
* **NumPy** (Math & Logic)
 
