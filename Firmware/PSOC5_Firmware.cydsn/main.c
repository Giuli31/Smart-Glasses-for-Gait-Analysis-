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
#include <stdio.h>
#include "project.h"
#include "Interrupt_Routines.h"
#include "Initialization.h"
#include "../src_shared/I2C_Interface.h"

int main(void)
{
    /*Enable communications:I2C [PSOC <--> LIS3DH] | UART [PSOC <--> HC-06]. */
    I2C_Peripheral_Start();
    UART_1_Start();
    /*Enable interrupts. */
    CyGlobalIntEnable; /* Enable global interrupts. */
    Pin_int_isr_StartEx(Custom_ISR_PIN);
    RX_isr_StartEx(Custom_ISR_RX);
    /*Initialization of the LEDs and LIS3DH accelerometer */
    INIT_LEDs();
    CHECK_LIS3DH();
    INIT_LIS3DH();
    CyDelay(5); 
    
    for(;;)
    {

    }
}

/* [] END OF FILE */
       
