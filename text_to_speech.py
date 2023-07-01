from constant import ELEVENLABS_API_KEY, VOICE_ID, CHUNK_SIZE
import requests

headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": f"{ELEVENLABS_API_KEY}"
    }


def run(text):
    """
    run: Generate audio from a text
    - text: input
    """
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
    
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    response = requests.post(url, json=data, headers=headers)
    with open('output.mp3', 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)


if __name__ == "__main__":
    sample = "First we thought the PC was a calculator. Then we found out how to turn numbers into letters and we thought it was a typewriter. And also I would like to test if you are enough good or fair for you to listen to this audio man, fuck you. I know you might think that i'm not kind, but consider that the team kittkat has built me, so it is not my fault."
    run(sample)