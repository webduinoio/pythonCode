from machine import I2S
from machine import Pin

audio_out = I2S(0,
                sck=Pin(13), ws=Pin(14), sd=Pin(17),
                mode=I2S.TX,
                bits=16,
                format=I2S.STEREO,
                rate=8000,
                ibuf=40000)

# create I2S object
wav = open('wav.wav','rb')

# advance to first byte of Data section in WAV file
pos = wav.seek(44) 

# allocate sample arrays
#   memoryview used to reduce heap allocation in while loop
wav_samples = bytearray(2048)
wav_samples_mv = memoryview(wav_samples)

print('Starting')

while True:
    try:
        num_read = wav.readinto(wav_samples_mv)
        num_written = 0
        if num_read == 0:
            pos = wav.seek(44) 
        else:
            while num_written < num_read:
                num_written += audio_out.write(wav_samples_mv[num_written:num_read], timeout=0)
    except (KeyboardInterrupt, Exception) as e:
        print('caught exception {} {}'.format(type(e).__name__, e))
        break
    
wav.close()
audio_out.deinit()
print('Done')