#include <arch/zx.h>
#include <stdio.h>
#include <string.h>

void main(void)
{
    // Set border color (white)
    zx_border(INK_WHITE);

    // Clear screen with black paper and white ink
    zx_cls(PAPER_BLACK | INK_WHITE);

    // Print text
    printf("Hello World!\n");
    printf("Proyecto LLMZ80\n");

    // Wait forever
    while (1)
        ; // Mantener texto en pantalla
}
