/* ========================================
 *
 * Copyright YOUR COMPANY, THE YEAR
 * All Rights Reserved
 * UNPUBLISHED, LICENSED SOFTWARE.
 *
 * CONFIDENTIAL AND PROPRIETARY INFORMATION
 * WHICH IS THE PROPERTY OF your company.
 *
 * ========================================
*/
#include "cytypes.h"
#include "Initialization.h"
#include "Pin_LED.h"
#include "LED_LIS3DH.h"
#include "UART_1.h"
#include "I2C_Master.h"
#include "../src_shared/I2C_Interface.h"
#include "../src_shared/LIS3DH.h"
#define LOW 0
#define HIGH 1
ErrorCode error;

/*  LED initialization function */
void INIT_LEDs() {
    Pin_LED_Write(LOW);
    LED_LIS3DH_Write(LOW);
}
/*  LIS3DH check connection  */
void CHECK_LIS3DH() {
    int32_t rval = I2C_Master_MasterSendStart(LIS3DH_DEVICE_ADDRESS, I2C_Master_WRITE_XFER_MODE);
    if( rval == I2C_Master_MSTR_NO_ERROR ) {
        //UART_1_PutString("LIS3DH found @ address 0x18\r\n");
        LED_LIS3DH_Write(LOW);
    }
    else {
        LED_LIS3DH_Write(HIGH);
    }
    I2C_Master_MasterSendStop();
}
/*  LIS3DH Initialization  */
void INIT_LIS3DH() {
    uint8_t axis_enable_data_rate = 0b01000111;
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH_CTRL_REG1,
                                         axis_enable_data_rate);
    // set FS +/- 2g
    uint8_t ctrl_reg4 = 0b00000000;   
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH_CTRL_REG4,
                                         ctrl_reg4);

    // setting FIFO register
    uint8 fifo_enable, fifo_FIFO, fifo_BYPASS, overrun_enable;
    // enable fifo
    error = I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS,
                                        LIS3DH__CTRL_REG5,
                                        &fifo_enable);
    fifo_enable = fifo_enable | 0b11000000;
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH__CTRL_REG5,
                                         fifo_enable);
    // put fifo in FIFO mode
    fifo_FIFO = 0b01000000;
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH__FIFO_CTRL_REG,
                                         fifo_FIFO);
    // overrun interrupt enable on INT_1 pin
    error = I2C_Peripheral_ReadRegister(LIS3DH_DEVICE_ADDRESS,
                                        LIS3DH_FIFO_CTRL_REG3,
                                        &overrun_enable);
    overrun_enable = overrun_enable | 0b00000010;
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH_FIFO_CTRL_REG3,
                                         overrun_enable);
    // reset FIFO registers content
    fifo_BYPASS = 0;
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH__FIFO_CTRL_REG,
                                         fifo_BYPASS);;
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,
                                         LIS3DH__FIFO_CTRL_REG,
                                         fifo_FIFO); 
}
/* [] END OF FILE */
