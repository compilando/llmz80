#include <cpctelera.h>

void initializeCPC()
{
    cpct_disableFirmware();
    cpct_setVideoMode(0);
    cpct_setBorder(HW_BLACK);
    cpct_clearScreen(0);

    u8 G_palette[16] = {
        HW_BLACK, HW_BLUE, HW_RED, HW_MAGENTA,
        HW_CYAN, HW_WHITE, HW_YELLOW, HW_BRIGHT_WHITE,
        HW_BLACK, HW_BLUE, HW_RED, HW_MAGENTA,
        HW_CYAN, HW_WHITE, HW_YELLOW, HW_BRIGHT_WHITE};
    cpct_fw2hw(G_palette, 16);
    cpct_setPalette(G_palette, 16);
}

void displayHola()
{
    u8 *pscreen = cpct_getScreenPtr(CPCT_VMEM_START, 20, 96);
    cpct_setDrawCharM0(4, 0);
    cpct_drawStringM0("HOLA", pscreen);
}

void main(void)
{
    initializeCPC();
    displayHola();
    while (1)
    {
        cpct_scanKeyboard_f();
        if (cpct_isKeyPressed(Key_Esc))
        {
            break;
        }
    }
}