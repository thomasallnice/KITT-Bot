const path = require("path");
const fs = require("fs");
const { Porcupine } = require("@picovoice/porcupine-node");
const { PvRecorder } = require("@picovoice/pvrecorder-node");
const { Configuration, OpenAIApi } = require("openai");
const wav = require('wav');
const voice = require('elevenlabs-node');

const playerOptions = {};

const player = require("play-sound")(playerOptions);

const RECORDING_LENGTH_MS = 5000;

const dotenvConfig = { path: path.resolve(__dirname, ".env") };
require("dotenv").config(dotenvConfig);
const PORCUPINE_KEY = process.env.PORCUPINE_KEY;

const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
  organization: process.env.OPENAI_ORG
});
const openai = new OpenAIApi(configuration);

const Mp32Wav = require('mp3-to-wav');
const { exec } = require("child_process");



const getResponse = async (message) => {
  const coffeeProcess=exec(`python3 /home/pi/Desktop/newwww/main.py "${message}"`)

  coffeeProcess.stdout.on('data', function(data) {
    console.log(data);
  });

}






const wakewordModelFile = path.resolve(__dirname, "models/wakeword/raspberry-pi.ppn");
const audioDeviceIndex = 1;

let handle = new Porcupine(PORCUPINE_KEY, [wakewordModelFile], [0.5]);

const frameLength = handle.frameLength;
const recorder = new PvRecorder(audioDeviceIndex, frameLength);
recorder.start();

console.log(`Using device: ${recorder.getSelectedDevice()}...`);

console.log(`Listening for wake word(s): "Hello KITT"`);

let isInterrupted = false;

process.on("SIGINT", function () {
  isInterrupted = true;
});

const startWordFile = path.resolve(__dirname, "./audio/yes_go_ahead.wav");


const transcribeAudio = async function (filename) {
  const transcript = await openai.createTranscription(
    fs.createReadStream(filename),
    "whisper-1"
  );
  return transcript.data.text;
}

const tempOutputFile = path.resolve(__dirname, "audio/user_speech.wav")

const onRecordingEnd = async () => {
  console.log("Recording stopped.");
  const userSpeechText = await transcribeAudio(tempOutputFile);
  console.log('User said:');
  console.log(`"${userSpeechText}"`)
  getResponse(userSpeechText);
}





const recordVoice = async () => {
  const frameLength = 512;
  const recorder = new PvRecorder(audioDeviceIndex, frameLength);
  recorder.start();
  console.log(`Recording, using: ${recorder.getSelectedDevice()}`);

  let isRecording = true;
  const timer = setTimeout(() => {
    isRecording = false;
    clearTimeout(timer);
  }, RECORDING_LENGTH_MS)

  let audio = [];
  while (isRecording) {
    const pcm = await recorder.read();
    audio = [...audio, ...pcm]
  }

  if (!isRecording) {
    const fileWriter = new wav.FileWriter(tempOutputFile, {
      channels: 1,
      sampleRate: 16000,
      bitDepth: 16,
    });

    fileWriter.on('finish', () => {
      console.log('File write complete.');
    });

    const buffer = Buffer.alloc(audio.length * 2); // Each audio sample is 2 bytes (16 bits)
    for (let i = 0; i < audio.length; i++) {
      buffer.writeInt16LE(audio[i], i * 2); // Write each audio sample as a 16-bit signed integer
    }

    fileWriter.write(buffer);
    fileWriter.end();
    recorder.release();
    onRecordingEnd();
  }

}

const runTicker = async () => {
  while (!isInterrupted) {
    const pcm = await recorder.read();
    let index = handle.process(pcm);
    if (index !== -1) {
      console.log(`Detected.`);
      player.play(startWordFile, (err) => {
        // Acknowledgement phrase finishes
        recordVoice();
        if (err) {
          console.log(error);
        }
      });
    }
  }
};

runTicker();
