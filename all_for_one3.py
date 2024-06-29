import RPi.GPIO as GPIO 
from time import sleep 
import datetime 
import requests 
from mfrc522 import SimpleMFRC522 
from hx711 import HX711 
from rpi_lcd import LCD 
from gpiozero import Servo 
from gpiozero.pins.pigpio import PiGPIOFactory 

GPIO.setmode(GPIO.BCM) #ตั้งโหมดการระบุพินเป็น BCM

lcd = LCD() #เริ่มต้นการใช้งานจอ LCD

#ตั้งพิน 13 และ 19 เป็น output สำหรับ LED
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)


#ตั้งค่าเซอร์โวบนพิน 18
pigpio_factory = PiGPIOFactory()
servo = Servo(18, pin_factory=pigpio_factory)

#ฟังก์ชันนี้ใช้ในการตั้งค่าเซ็นเซอร์ inductive บนพินที่ระบุ
def initialInductive(pin):
  global GPIOpin 
  GPIOpin = pin 
  GPIO.setmode(GPIO.BCM) 
  GPIO.setup(GPIOpin,GPIO.IN, pull_up_down=GPIO.PUD_DOWN) 

  

#ตั้งค่าพิน 20 และ 21 เป็น input สำหรับเซ็นเซอร์
GPIO.setup(20, GPIO.IN)
GPIO.setup(21, GPIO.IN)


reader = SimpleMFRC522()

#sending data
data_to_send = {}
data_to_send["date"] = str(datetime.datetime.now())
 
#Loadcell
hx = HX711(5, 6) 
hx.set_reading_format("MSB", "MSB") 


referenceUnit = 114 
hx.set_reference_unit(716) 


hx.reset() 
hx.tare()


set1 = 0
set2 = 0


while True:
    
    lcd.text("  Bin Bin Project!",2)
    lcd.text("  Let's Start!",3)
    print("Start!")
    
    
    servo.value = 0.5

    try:
        id, text = reader.read()
        print(id)
        print(text)
        plastic = 0
        glass = 0
        can = 0
        wrong = 0
        data_to_send["id"] = str(id)
        data_to_send["user"] = text
        
    except (KeyboardInterrupt, SystemExit):
        GPIO.cleanup()
        cleanAndExit()

    finally:
        while True:
            servo.value = 0.5
            
            initialInductive(17)
            initialInductive(27)
    
            sensor = GPIO.input(20)
            check = GPIO.input(21)
            induc = GPIO.input(17)
            induc2 = GPIO.input(27)
            
            #Check with Load cell
            val = hx.get_weight(5) * (-1)
            print(val)
            hx.power_down()
            hx.power_up()
            sleep(0.5)
            
            
            if sensor == 0:
                lcd.text("User: " + text,1)
                lcd.text("Plastic Bt. : " + str(plastic),2)
                lcd.text("Glass Bt. : " + str(glass),3)
                lcd.text("Can : " + str(can),4)
                
                #can scanner
                if induc == 0 and check == 0:
                    can += 1
                    sleep(0.1)
                    print("Can: " + str(can))
                    lcd.text("Can : " + str(can),4)
                    sleep(1)
                    
                elif induc == 1 and check == 0:
                    wrong += 1
                    set2 = 1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             
                    sleep(0.1)
                    print("Wrong: " + str(wrong))
                    
                elif val >= 100:
                    servo.value = 0
                    sleep(0.5)
                    glass += 1
                    sleep(1)
                    lcd.text("Glass Bt. : " + str(glass),3)
                    
                elif val >= 5:
                    servo.value = 0.3
                    sleep(1)
                    if induc2 == 0:
                        servo.value = 1 
                        sleep(1)
                        wrong += 1
                        set1 = 1
                        sleep(1)
                        print("Wrong: " + str(wrong))
                    else:
                        servo.value = 1
                        sleep(0.5)
                        plastic += 1
                        sleep(1)
                        lcd.text("Plastic Bt. : " + str(plastic),2)
                    
                else:
                    pass
    
            elif sensor == 1:
                data_to_send["Plastic Bt."] = plastic
                data_to_send["Glass Bt."] = glass
                data_to_send["Can"] = can
                data_to_send["Wrong"] = wrong
                lcd.clear()
                print("Sending Data...")
                lcd.text("  Sending Data...",2)
                sleep(1)
                r = requests.post("https://hook.eu2.make.com/2l1terlrvwsuum568s6rfrujllrpfsa7", json = data_to_send)
                print(r.status_code)
                print("Complete")
                lcd.clear()
                sleep(1)
                lcd.text("     Complete!",2)
                sleep(2)
                lcd.clear()
                break
    if set1 == 1:
        GPIO.output(13, GPIO.HIGH)
    if set2 == 1:
        GPIO.output(19, GPIO.HIGH)


