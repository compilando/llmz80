// Description: Initializes the Amstrad CPC by disabling firmware, setting video mode 0, configuring character drawing colors, and then enters an infinite loop for further execution.
#include <cpctelera.h>

//
// Set up the Amstrad
//
void initialize_cpc()
{
   cpct_disableFirmware();   // Disable firmware to prevent it from interfering with setPalette and setVideoMode
   cpct_setVideoMode(0);     // Set video mode 0 (160x200, 16 colours)
   cpct_setDrawCharM0(3, 0); // Set PEN 3, PAPER 0 for Characters to be drawn using cpct_drawCharM0
}

void main(void)
{
   initialize_cpc(); // Initialize the CPC

   //
   // Infinite loop
   //
   while (1)
   {
      // Aqui va el programa principal
   }
}
