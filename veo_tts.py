import replicate
from deep_translator import GoogleTranslator
from moviepy.editor import VideoFileClip
import os
import requests

REPLICATE_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_TOKEN:
    raise RuntimeError("❌ REPLICATE_API_TOKEN is not set. Please export it in env.")

def generate_veo_tts(text, voice="grandmother", lang="kazakh", out_dir="output"):
    os.makedirs(out_dir, exist_ok=True)

    # 1. Translate input text to English
    translated = GoogleTranslator(source='auto', target='en').translate(text)

    # 2. Select voice description
    voice = voice.lower()
    if voice == "grandmother":
        subject = "She"
        descriptor = "soft, familiar voice of a grandmother"
    elif voice == "female":
        subject = "She"
        descriptor = "clear, gentle female voice"
    elif voice == "grandfather":
        subject = "He"
        descriptor = "deep, calm masculine voice of a grandfather"
    elif voice == "male" or voice == "man":
        subject = "He"
        descriptor = "confident, strong male voice"
    else:
        subject = "They"
        descriptor = "soft, neutral voice"

    # 3. Prepare prompt
    prompt = (
        f"The black screen is silent, save for the {descriptor}. "
        f"{subject} speaks in the {lang} language:\n\n"
        f'"{translated}"'
    )

    print("📤 Sending VEO3 prompt...")
    # 4. Generate video using Replicate
    output = replicate.run(
        "google/veo-3",
        input={"prompt": prompt}
    )

    # 5. Save video from URL
    video_url = next(output)
    video_path = os.path.join(out_dir, "output.mp4")
    r = requests.get(video_url)
    with open(video_path, "wb") as f:
        f.write(r.content)

    print(f"🎞 Video saved: {video_path}")

    # 6. Extract audio if available
    audio_path = os.path.join(out_dir, "output.mp3")
    video = VideoFileClip(video_path)
    if video.audio:
        video.audio.write_audiofile(audio_path)
        print(f"🔊 Audio ready: {audio_path}")
    else:
        print("⚠️ No audio track found in the video.")
    return audio_path

if __name__ == "__main__":
    generate_veo_tts(
        text="This is an example text in Kazakh. You can use any language.",
        voice="grandmother",  # or "female", "grandfather", "male"
        lang="kazakh"
    )