#include <cpctelera.h>

void main(void) {
    // Initialize CPCtelera
    cpct_disableFirmware();
    cpct_setVideoMode(1);
    
    // Clear screen (black background)
    cpct_memset(CPCT_VMEM_START, 0x00, 0x4000);
    
    // Set text properties
    cpct_setDrawCharM1(3, 0);   // White text on black background
    
    // Print text at coordinates (10, 10)
    cpct_drawStringM1("Hello World!", CPCT_VMEM_START + 80*10 + 10);
    
    // Wait forever
    while(1) {
        cpct_waitVSYNC();
    }
}
