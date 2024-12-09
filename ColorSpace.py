import cv2
import numpy as np

def bgr_to_rgb(img):
    return img[..., ::-1]

def rgb_to_bgr(img):
    return img[..., ::-1]

def rgb_to_hsv(img):
    # Normalizacjia wartości do zakresu [0, 1]
    img = img.astype('float32') / 255.0
    h, w, _ = img.shape
    hsv = np.zeros((h, w, 3), dtype='float32')
    
    # pętla która zmienia wartość każdego pixela w zdjęciu
    for i in range(h):
        for j in range(w):
            r, g, b = img[i, j]
            mx = max(r, g, b)
            mn = min(r, g, b)
            diff = mx - mn

            # obliczenie Hue
            if diff == 0:
                h_val = 0
            elif mx == r:
                h_val = (60 * ((g - b) / diff) + 360) % 360 #dałem modulo by były wartości w zakresie
            elif mx == g:
                h_val = (60 * ((b - r) / diff) + 120) % 360
            elif mx == b:
                h_val = (60 * ((r - g) / diff) + 240) % 360

            # Obliczanie Saturatuion
            s_val = 0 if mx == 0 else (diff / mx)
            
            # Obliczanie Value
            v_val = mx

            # Skalowanei Hue do [0, 179], Saturacja i Value do [0,255] bo tak robi openCV i inaczej nie działa dobrze
            hsv[i, j] = [h_val / 2, s_val * 255, v_val * 255]

    return hsv

def hsv_to_rgb(img):
    img = img.astype('float32')
    h, w, _ = img.shape
    rgb = np.zeros((h, w, 3), dtype='float32')
    
    # pętla która zmienia wartość każdego pixela w zdjęciu
    for i in range(h):
        for j in range(w):
            h_val, s_val, v_val = img[i, j]
            h_val *= 2  # skalowanie Hue do [0, 360]
            s_val /= 255  # Skalowanie Saturation do [0, 1]
            v_val /= 255  # Skalowanie Value do [0, 1]

            c = v_val * s_val
            x = c * (1 - abs((h_val / 60) % 2 - 1))
            m = v_val - c
            
            # Derterminowanie RGB na podstawie Hue
            if 0 <= h_val < 60:
                r, g, b = c, x, 0
            elif 60 <= h_val < 120:
                r, g, b = x, c, 0
            elif 120 <= h_val < 180:
                r, g, b = 0, c, x
            elif 180 <= h_val < 240:
                r, g, b = 0, x, c
            elif 240 <= h_val < 300:
                r, g, b = x, 0, c
            else:
                r, g, b = c, 0, x
            
            rgb[i, j] = [(r + m) * 255, (g + m) * 255, (b + m) * 255]
    
    return rgb

def rgb_to_yuv(img):
    img = img.astype('float32')
    yuv = np.zeros_like(img, dtype='float32')
    
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            r, g, b = img[i, j]
            y = 0.299*r + 0.587*g + 0.114*b
            u = -0.14713*r - 0.28886*g + 0.436*b + 128
            v = 0.615*r - 0.51499*g - 0.10001*b + 128
            yuv[i, j] = [y, u, v]
    
    return yuv

def yuv_to_rgb(img):
    img = img.astype('float32')
    rgb = np.zeros_like(img, dtype='float32')
    
    for i in range(img.shape[0]):
        for j in range(img.shape[1]):
            y, u, v = img[i, j]
            u -= 128
            v -= 128
            r = y + 1.13983*v
            g = y - 0.39465*u - 0.58060*v
            b = y + 2.03211*u
            rgb[i, j] = [r, g, b]
    
    return rgb

# Zmiana Jasności obrazu w YUV
def adjust_brightness_yuv(img, brightness_factor):
    if brightness_factor < -1 or brightness_factor > 1:
        raise ValueError("Brightness factor should be between -1 and 1")
    
    img = img.astype('float32')
    adjusted_img = np.copy(img)
    
    adjusted_img[:, :, 0] = np.clip(adjusted_img[:, :, 0] + brightness_factor * 255, 0, 255)
    
    return adjusted_img

# ładowanie obrazu
try:
    image = cv2.imread('img.jpg')
    if image is None:
        raise FileNotFoundError("The image file was not found")
    
    # konwersja obrazu bgr do rgb
    resized_rgb_image = bgr_to_rgb(image)
except Exception as e:
    print(f"Error loading image: {e}")
    exit()

try:
    #Konwersja obrazu do HSV i zapisanie go
    hsv_image = rgb_to_hsv(resized_rgb_image)
    cv2.imwrite('hsv_image.jpg', hsv_image)
    
    #Konwersja obrazu z HSV do RGB i zapisanie go
    rgb_from_hsv = hsv_to_rgb(hsv_image)
    rgb_from_hsv_bgr = rgb_to_bgr(rgb_from_hsv)
    cv2.imwrite('rgb_from_hsv.jpg', rgb_from_hsv_bgr)
    
    #Konwersja obrazu do YUV i zapisanie go
    yuv_image = rgb_to_yuv(resized_rgb_image)
    cv2.imwrite('yuv_image.jpg', yuv_image)
    
    # zwiększenie jasności obrazu YUV i zapisanie go
    adjusted_yuv = adjust_brightness_yuv(yuv_image, 0.2)  # Example: Increase brightness by 0.2
    cv2.imwrite('adjusted_yuv_image.jpg', adjusted_yuv)
    
    # Konwersja obrazu z YUV do RGB i zapisanie go
    rgb_from_yuv = yuv_to_rgb(adjusted_yuv)
    rgb_from_yuv_bgr = rgb_to_bgr(rgb_from_yuv)
    cv2.imwrite('rgb_from_yuv.jpg', rgb_from_yuv_bgr)
    
except Exception as e:
    print(f"Error processing image: {e}")
    exit()
