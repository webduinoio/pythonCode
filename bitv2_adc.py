from machine import ADC,Pin
import utime


adc = ADC(Pin(12)) # 声明ADC对象 设置D34号引脚作为ADC采样引脚
adc.atten(ADC.ATTN_11DB) # 设置衰减比 满量程3.3v
adc.width(ADC.WIDTH_10BIT) # 设置数据宽度为10bit
print(adc.read())