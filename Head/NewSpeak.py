from gtts import gTTS #pip install gtts
import pygame
import io
import time
import os

def speak(text, lang="en"):
    try:
        # Try multiple TLD options if one fails
        tlds = ['com.au', 'com', 'co.uk', 'ca']
        last_error = None
        
        for tld in tlds:
            try:
                tts = gTTS(text=text, tld=tld, lang=lang, slow=False)
                mp3_fp = io.BytesIO()
                tts.write_to_fp(mp3_fp)
                mp3_fp.seek(0)
                
                pygame.mixer.init()
                pygame.mixer.music.load(mp3_fp, 'mp3')
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                return True
            except Exception as e:
                last_error = e
                continue
        
        # If all TLDs fail, just return False silently
        return False
            
    except Exception as e:
        return False

# Test the function
if __name__ == "__main__":
    speak("Testing text to speech functionality")

# speak("hello my name is jarvis")