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
#ifndef __INTERRUPT_ROUTINES_H
    
    #define __INTERRUPT_ROUTINES_H
    
    #include "cytypes.h"
    #include "stdio.h" 

    // CALL isr function PIN
    CY_ISR_PROTO(Custom_ISR_PIN);
    
    // CALL isr function TIMER
    CY_ISR_PROTO(Custom_ISR_TIMER);
    
    // CALL isr function RX
    CY_ISR_PROTO(Custom_ISR_RX);
    
#endif
/* [] END OF FILE */
