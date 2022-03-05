
import os
from machine import I2S
from machine import Pin

# ======= I2S CONFIGURATION =======
SCK_PIN = 13
WS_PIN = 14
SD_PIN = 17
I2S_ID = 0
WAV_FILE = "1.wav"

audio_out = I2S(
    I2S_ID,
    sck=Pin(SCK_PIN),ws=Pin(WS_PIN),sd=Pin(SD_PIN),
    mode   = I2S.TX,
    bits   = 16,
    format = I2S.MONO,
    #format = I2S.STEREO,
    rate   = 8000,
    ibuf   = 10000,
)

wav = open(WAV_FILE, "rb")
pos = wav.seek(44)  # advance to first byte of Data section in WAV file

# allocate sample array
# memoryview used to reduce heap allocation
wav_samples = bytearray(10000)
wav_samples_mv = memoryview(wav_samples)

# continuously read audio samples from the WAV file
# and write them to an I2S DAC
print("==========  START PLAYBACK ==========")
try:
    i = 0;
    while True:
        num_read = wav.readinto(wav_samples_mv)
        i = i + num_read
        print(str(i/1024.0)+" KBytes")
        # end of WAV file?
        if num_read == 0:
            # end-of-file, advance to first byte of Data section
            # _ = wav.seek(44)
            break;
        else:
            _ = audio_out.write(wav_samples_mv[:num_read])

except (KeyboardInterrupt, Exception) as e:
    print("caught exception {} {}".format(type(e).__name__, e))

# cleanup
wav.close()
audio_out.deinit()
print("Done")