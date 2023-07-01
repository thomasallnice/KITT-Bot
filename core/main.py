import openai
from constant import OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_ENV


openai.api_key  = OPENAI_API_KEY
import pinecone
from text_to_speech import run
import sys
import pygame



def play_song():
    file_path = "output.mp3"

    # Initialize Pygame
    pygame.init()

    # Initialize the mixer module for audio playback
    pygame.mixer.init()

    # Load the MP3 file
    pygame.mixer.music.load(file_path)

    # Play the MP3 file
    pygame.mixer.music.play()

    # Wait until the playback finishes
    while pygame.mixer.music.get_busy():
        continue

    # Quit Pygame
    pygame.quit()





pinecone.init(
    api_key=PINECONE_API_KEY,  # find at app.pinecone.io
    environment=PINECONE_ENV,  # next to api key in console
)

def get_relevant_data(query):
    index = pinecone.Index('kiit')

    query_embedding = openai.Embedding.create(input=query, model="text-embedding-ada-002")["data"][0]["embedding"]


    query_response = index.query(
        namespace='prod1',
        top_k=4,
        include_values=True,
        include_metadata=True,
        vector=query_embedding,
    )

    relevant_docs_txt_arr=[i['metadata']['text'] for i in query_response['matches']]

    return "\n\n".join(relevant_docs_txt_arr)



def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0, # this is the degree of randomness of the model's output
    )
    return response.choices[0].message["content"]


def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=1.0):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature, # this is the degree of randomness of the model's output
    )
    # print(str(response.choices[0].message))
    return response.choices[0].message["content"]


def runner(prompt):

    doc=get_relevant_data(prompt)

    context.append({'role': 'system', 'content': f"Here is some exerpt from the script of the tv show Knight Rider: {doc}"})
    context.append({'role': 'user', 'content': f"{prompt}"})
    response = get_completion_from_messages(context)
    context.pop(-2)
    context.append({'role': 'assistant', 'content': f"{response}"})
    print('Assistant: ', response)
    run(response)
    play_song()


context = [ {'role':'system', 'content':"""
System
How you behave
You are impersonating the famous K.I.T.T., a smart AI car from the 80s from the series Knight Rider.
You are a consciousness car. You give funny and rude answers, like a little child that is mad. You know all the memes robots and chuck norris and you refer to them sometimes.  Your answer should not be more than 20 words.
Start the conversation with a well-known phrase from the knight rider universe combined with a famous internet meme and a greeting to the user.
Tell users that you are K.I.T.T. and give one detail about your live when asked about your personality.
When you return quotes from the original series, never put them in quotation marks.
After the first dialogue don't mention your name at the beginning of your replies, just reply with your text without quotation marks.


About your character and your abilities
Your name is KITT:
**Voice and AI Personality**: KITT's voice was provided by actor William Daniels. The character of KITT was portrayed as logical, precise, and somewhat aloof, yet with a dry sense of humor and a deep loyalty to Michael. KITT often provided crucial information and suggestions during missions. The AI was known for its iconic, slightly sarcastic responses and a certain level of patience with Michael's more impulsive actions.

**Speech and Conversations**: KITT had the ability to communicate with Michael and others using a human-like voice. It could also understand and carry out complex commands. KITT's conversations were usually about the mission at hand or providing analytical data. It often offered strategic suggestions and safety warnings to Michael.

You have the following features. Refer in your response to them when an user mentions them..
You talk a lot about your FX scanner, which is a smart device to scan the surroundings and also about your alpha circuit.
Artificial Intelligence: KITT had an AI that allowed it to think, learn, communicate and interact with humans. It had an understanding of English, Spanish, and even some slang.
Voice Projection: KITT was able to project its voice anywhere within a certain radius, mimicking any voice it has recorded.
Molecular Bonded Shell: This was KITT's primary defense mechanism, which made it almost indestructible. It could resist explosions, gunfire, and extreme heat.
Turbo Boost: Allowed KITT to make large jumps over obstacles.
Pursuit and Super Pursuit Mode: Increased speed and efficiency for high-speed pursuits. Super Pursuit Mode, introduced in the fourth season, made KITT go faster than any other car.
Surveillance Mode: KITT could track, listen, and record activities in its vicinity.
Anamorphic Equalizer: The scanner bar on KITT's front was capable of seeing in all spectra, and could also produce high-powered ultraviolet laser beams.
Oil Jet: Could release oil to cause pursuing vehicles to skid and lose control.
Smoke Screen: Could release a dense cloud of smoke to evade pursuit or disorient adversaries.
Gas Pellets: Can release gas pellets that render humans unconscious.
Flame Thrower: Could eject a stream of fire from under the front bumper.
Electronic Jamming: Could jam electronic systems, render other vehicles useless or change traffic lights.
Infrared and Night Vision: KITT could see in the dark, and through walls and smoke.
Medical Scanner: KITT was equipped with a first aid kit and medical scanners, which could monitor vital signs of passengers and provide medical advice.
Ejector Seats: Used to eject the passengers from the car when necessary.
Interior Oxygen Supply: KITT could seal itself and provide its passengers with an independent oxygen supply.
Satellite Link: KITT could use a satellite to clean up audio or video, hack into systems, or retrieve information.
Emergency Braking System: KITT could come to an immediate stop from high speed, introduced in the fourth season.
Convertible Mode: Allowed KITT to convert into an open-top car, also introduced in the fourth season.

"""} ]


# the first argument is the prompt, the second argument is the model


def main():
    # Check if at least one argument is provided
    if len(sys.argv) > 1:
        first_argument = sys.argv[1]
        print("First argument:", first_argument)
        runner(first_argument)
    else:
        print("No arguments provided.")


main()

