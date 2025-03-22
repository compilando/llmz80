#include <cpctelera.h>

void main(void) {
    // Initialize CPCtelera
    cpct_disableFirmware();
    
    // Clear screen
    cpct_clearScreen();
    
    // Set text mode
    cpct_setVideoMode(0);
    
    // Set text colors (white on black)
    cpct_setInkGphStr(3, 0);
    
    // Draw text
    cpct_drawStringM1("Hello World!");
    
    // Wait forever
    while(1);
}
