# STM32 Custom Bootloader
In this project a custom bootloader written and uploaded to the microcontroller. with this bootlader we can program stm32f103 microcontroller over USB connection.

For programming microcontroller a CLI application implemented in python. python app communicates with the microcontroller and it can read, erase and write to the flash memory (in application part). 

* Erase Main App Flash: `python custom_stm32_programmer.py --com-port <COM PORT> -e`

* Write application bin file to Main App Flash: 
`python custom_stm32_programmer.py --com-port <COM PORT> -w "<Path to bin file>"`
