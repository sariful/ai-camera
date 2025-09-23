import os
import pygame

script_dir = os.path.dirname(os.path.abspath(__file__))

def sound_alert():
    try:
        pygame.mixer.init()
        sound_path = os.path.join(script_dir, "../assets/beep-329314.mp3")
        pygame.mixer.music.load(sound_path)
        pygame.mixer.music.play()
    except Exception as e:
        print(f"⚠️ Error playing sound: {e}")

if __name__ == "__main__":
    sound_alert()