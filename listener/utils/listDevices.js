const { PvRecorder } = require("@picovoice/pvrecorder-node");
const devices = PvRecorder.getAudioDevices();
console.log(devices);
process.exit();
