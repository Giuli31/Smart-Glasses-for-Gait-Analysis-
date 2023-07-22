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
#include "project.h"
#include "Interrupt_Routines.h"
#include "Pin_LED.h"
#include "Timer_1.h"
#include "../src_shared/I2C_Interface.h"
#include "../src_shared/LIS3DH.h"
#include "UART_1.h"
#define HIGH 1
#define LOW 0

uint8_t vect_to_send[194],j,fifo_FIFO = 0b01000000;
int8_t enable_send=-1,ready=0;
ErrorCode error;

/*  RX interrupt isr code  */
CY_ISR(Custom_ISR_RX) {
    char ch_received = UART_1_GetChar();
    switch(ch_received) {
        // LED lampeggia 1 Hz quando esiste connessione bluethoot con GUI: in attessa di start acquisition    
        case  'A':
        case  'a':
        Timer_1_Start();
        Timer_isr_StartEx(Custom_ISR_TIMER);
        enable_send = 0;
        ready = 1;
        break;
        // LED ON fisso duarante l'acqusizione
        case 'B':
        case 'b':
        if (ready == 1) {
        enable_send = 1;
        Timer_1_Stop();
        Pin_LED_Write(HIGH);
        }
        // LED off: connessione persa
        break;
        case 'C':
        case 'c':
        enable_send = -1;
        ready = 0;
        Timer_1_Stop();
        Pin_LED_Write(LOW);
        break;
        default:
        break;
    }
}
/*  PIN_interrupt isr code  */
CY_ISR(Custom_ISR_PIN) {
    vect_to_send[0] = 0xA0;  // header
    vect_to_send[193] = 0xC0;  // tail
            for (int j=1;j<193;j=j+6) {
                error = I2C_Peripheral_ReadRegisterMulti(LIS3DH_DEVICE_ADDRESS,
                                               LIS3DH_OUT_X_L,
                                               6,
                                               &vect_to_send[j]);
            }
    //reset FIFO register content
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH__FIFO_CTRL_REG,0);                                
    error = I2C_Peripheral_WriteRegister(LIS3DH_DEVICE_ADDRESS,LIS3DH__FIFO_CTRL_REG,fifo_FIFO); 
    //Data are sent every 1/50 * 32 [s] during acquisition phase                                                                   
    if (enable_send == 1) {
           UART_1_PutArray(vect_to_send,194);
        }
    //If devices are paired and ready to start acquisition the string below is sent every 1/50 * 32 [s]
    else if (enable_send == 0) {
            UART_1_PutString("Ready to start acquisition\r\n");
        }
    //If device is ready to pair the string below is sent every 1/50 * 32 [s]
    else if (enable_send == -1) {
                 UART_1_PutString("Ready\r\n");
        }  
    Pin_int_ClearInterrupt();
}
/*  Timer isr 1Hz used to blink the green LED  */
CY_ISR(Custom_ISR_TIMER) {
   Pin_LED_Write(~Pin_LED_Read());
    Timer_1_ReadStatusRegister();
}
   
/* [] END OF FILE */
