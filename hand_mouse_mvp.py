"""
Hand Tracking Mouse Control MVP
Uses OpenCV + MediaPipe to control mouse via hand gestures.
Requires: pip install opencv-python mediapipe pynput
"""

import cv2
import mediapipe as mp
from mediapipe.tasks.python.vision import HandLandmarker, RunningMode, HandLandmarkerOptions
from mediapipe.tasks.python.core import base_options
import numpy as np
from pynput.mouse import Controller, Button
import time
import os


class HandMouseController:
    def __init__(self):
        self.mouse = Controller()
        self.cap = cv2.VideoCapture(0)
        
        # MediaPipe hand landmarker setup
        self.cam_width, self.cam_height = 640, 480
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cam_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cam_height)
        
        # Download model if needed
        model_path = self._get_model_path()
        
        options = HandLandmarkerOptions(
            base_options=base_options.BaseOptions(model_asset_path=model_path),
            running_mode=RunningMode.VIDEO,
            num_hands=1,
            min_hand_detection_confidence=0.5,
            min_hand_presence_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.landmarker = HandLandmarker.create_from_options(options)
        
        # Screen dimensions
        self.screen_width, self.screen_height = 1920, 1080
        try:
            import pyautogui
            self.screen_width, self.screen_height = pyautogui.size()
        except:
            pass
        
        # Smoothing and state
        self.prev_x, self.prev_y = 0, 0
        self.smoothing = 0.5
        self.click_threshold = 0.05
        self.is_clicking = False
        self.click_cooldown = 0.3
        self.last_click_time = 0
        self.frame_timestamp = 0
    
    def _get_model_path(self):
        """Get or download the hand landmarker model."""
        model_path = "hand_landmarker.task"
        if not os.path.exists(model_path):
            print("Downloading hand landmarker model...")
            import urllib.request
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
            print("Model downloaded!")
        return model_path
    
    def get_distance(self, p1, p2):
        """Calculate distance between two landmarks."""
        return np.sqrt((p1.x - p2.x) ** 2 + (p1.y - p2.y) ** 2)
    
    def map_to_screen(self, x, y):
        """Map normalized camera coordinates to screen coordinates."""
        screen_x = int((1 - x) * self.screen_width)
        screen_y = int(y * self.screen_height)
        return screen_x, screen_y
    
    def smooth_move(self, x, y):
        """Apply smoothing to mouse movement."""
        new_x = int(self.prev_x * self.smoothing + x * (1 - self.smoothing))
        new_y = int(self.prev_y * self.smoothing + y * (1 - self.smoothing))
        self.prev_x, self.prev_y = new_x, new_y
        return new_x, new_y
    
    def detect_pinch(self, landmarks):
        """Detect pinch gesture between thumb and index finger."""
        thumb_tip = landmarks[4]  # THUMB_TIP
        index_tip = landmarks[8]  # INDEX_FINGER_TIP
        distance = self.get_distance(thumb_tip, index_tip)
        return distance < self.click_threshold
    
    def draw_landmarks(self, frame, landmarks):
        """Draw hand landmarks on frame."""
        h, w = frame.shape[:2]
        for lm in landmarks:
            cx, cy = int(lm.x * w), int(lm.y * h)
            cv2.circle(frame, (cx, cy), 3, (0, 255, 0), -1)
        
        # Draw connections
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
        ]
        for start, end in connections:
            if start < len(landmarks) and end < len(landmarks):
                x1, y1 = int(landmarks[start].x * w), int(landmarks[start].y * h)
                x2, y2 = int(landmarks[end].x * w), int(landmarks[end].y * h)
                cv2.line(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
    
    def run(self):
        print("Hand Tracking Mouse Control")
        print("===========================")
        print("1. Show your hand to the camera")
        print("2. Move hand to control cursor (mirrored movement)")
        print("3. Pinch thumb + index finger to CLICK")
        print("Press 'Q' to quit")
        print()
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to capture frame")
                break
            
            # Flip frame for natural interaction
            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Convert to MediaPipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Detect hands
            self.frame_timestamp += 1
            result = self.landmarker.detect_for_video(mp_image, self.frame_timestamp)
            
            status = "No hand detected"
            
            if result.hand_landmarks:
                landmarks = result.hand_landmarks[0]
                
                # Draw landmarks
                self.draw_landmarks(frame, landmarks)
                
                # Get index finger tip position
                index_tip = landmarks[8]
                screen_x, screen_y = self.map_to_screen(index_tip.x, index_tip.y)
                smooth_x, smooth_y = self.smooth_move(screen_x, screen_y)
                
                # Move mouse
                self.mouse.position = (smooth_x, smooth_y)
                
                # Detect pinch
                is_pinching = self.detect_pinch(landmarks)
                current_time = time.time()
                
                if is_pinching and not self.is_clicking:
                    if current_time - self.last_click_time > self.click_cooldown:
                        self.mouse.press(Button.left)
                        self.is_clicking = True
                        self.last_click_time = current_time
                        status = "HOLDING CLICK"
                elif not is_pinching and self.is_clicking:
                    self.mouse.release(Button.left)
                    self.is_clicking = False
                    status = "RELEASED"
                elif is_pinching:
                    status = "PINCH (holding)"
                else:
                    status = f"Tracking - x:{smooth_x}, y:{smooth_y}"
                
                # Visual feedback
                h, w = frame.shape[:2]
                pinch_color = (0, 0, 255) if is_pinching else (0, 255, 0)
                cx, cy = int(index_tip.x * w), int(index_tip.y * h)
                cv2.circle(frame, (cx, cy), 10, pinch_color, -1)
            
            # Display status
            cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                       0.7, (255, 255, 255), 2)
            cv2.putText(frame, "Press 'Q' to quit", (10, frame.shape[0] - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
            
            cv2.imshow('Hand Mouse Control', frame)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cleanup()
    
    def cleanup(self):
        """Release resources."""
        self.cap.release()
        cv2.destroyAllWindows()
        self.landmarker.close()
        print("\nShutdown complete")


def main():
    try:
        controller = HandMouseController()
        controller.run()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
