import cv2
import numpy as np

def enhance_image(img):
    """
    Enhance image for better detection
    Handles: low light, rain, blur, shadows
    """
    # Step 1: Denoise
    denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)

    # Step 2: Enhance contrast using CLAHE
    lab = cv2.cvtColor(denoised, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    enhanced = cv2.merge([l, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    # Step 3: Sharpen
    kernel = np.array([[-1,-1,-1],
                       [-1, 9,-1],
                       [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)

    return sharpened

def detect_night_mode(img):
    """
    Check if image is dark (night)
    """
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    avg_brightness = np.mean(gray)
    return avg_brightness < 80  # True = night

def enhance_night(img):
    """
    Brighten dark/night images
    """
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v = cv2.add(v, 60)  # Increase brightness
    final = cv2.merge([h, s, v])
    return cv2.cvtColor(final, cv2.COLOR_HSV2BGR)

def preprocess(image_path):
    """
    Full preprocessing pipeline
    """
    # Read image
    img = cv2.imread(image_path)

    if img is None:
        raise ValueError(f"Could not read image: {image_path}")

    # Check if night
    is_night = detect_night_mode(img)

    if is_night:
        print("🌙 Night mode detected - enhancing brightness")
        img = enhance_night(img)

    # Enhance image
    img = enhance_image(img)

    print(f"✅ Preprocessing done | Night mode: {is_night}")
    return img, is_night

if __name__ == "__main__":
    print("✅ Preprocessing module ready!")