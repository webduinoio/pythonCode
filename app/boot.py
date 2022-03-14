from machine import Pin, PWM
pwm = PWM(Pin(2))
pwm.freq(1024)
pwm.duty(3)
