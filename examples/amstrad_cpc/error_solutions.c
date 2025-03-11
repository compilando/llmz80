/**
 * @file error_solutions.c
 * @brief Soluciones a errores comunes en el desarrollo para Amstrad CPC
 *
 * Este archivo contiene ejemplos de código que muestran cómo solucionar
 * los errores más comunes que pueden surgir al desarrollar para Amstrad CPC
 * usando CPCtelera y SDCC.
 */

// SOLUCIÓN: Incluir cpctelera.h para poder usar tipos como u8, u16, etc.
#include <cpctelera.h>

// SOLUCIÓN: Definir constantes con nombres significativos para direcciones de memoria
#define SCREEN_START 0xC000
#define OFFSET_LINE_50 0x0400
#define SCREEN_WIDTH 80
#define SCREEN_HEIGHT 200

// SOLUCIÓN: Definir la paleta como un array de tamaño fijo
const u8 g_palette[16] = {
    0, 3, 6, 9, 12, 15, 18, 21,
    24, 26, 28, 30, 31, 22, 14, 6};

/**
 * SOLUCIÓN: Definir estructuras correctamente con typedef
 * Error común: syntax error: token -> 'Node' o 'char'
 */
typedef struct
{
    u8 x;
    u8 y;
    u8 color;
} Sprite;

/**
 * SOLUCIÓN: No hay malloc en Z80/CPCtelera, usar arrays estáticos
 * Error común: function 'malloc' implicit declaration, too many parameters
 */
#define MAX_SPRITES 10
Sprite sprites_pool[MAX_SPRITES];
u8 next_free_sprite = 0;

/**
 * @brief Función para "asignar" un sprite del pool
 *
 * SOLUCIÓN: Implementar un gestor de memoria simple
 */
Sprite *allocate_sprite()
{
    if (next_free_sprite < MAX_SPRITES)
    {
        return &sprites_pool[next_free_sprite++];
    }
    return NULL; // No hay más sprites disponibles
}

/**
 * @brief Dibuja un rectángulo en la pantalla
 *
 * SOLUCIÓN: Usar casting explícito para direcciones de memoria
 */
void drawRectangle(u8 x, u8 y, u8 width, u8 height, u8 color)
{
    // Calcular la dirección de memoria
    u16 offset = y * SCREEN_WIDTH + x;

    // SOLUCIÓN: Usar casting explícito para convertir integral a puntero
    // Mal: cpct_drawSolidBox(SCREEN_START + offset, color, width, height);
    // Bien:
    cpct_drawSolidBox((void *)(SCREEN_START + offset), color, width, height);
}

/**
 * @brief Función principal
 */
void main(void)
{
    // SOLUCIÓN: Declarar todas las variables al principio de la función
    // Error común: Undefined identifier 'response' o 'root'
    char response[20] = "OK";
    u8 restart = 0;

    // Desactivar firmware para tener control total
    cpct_disableFirmware();

    // Establecer modo de vídeo (1 = 320x200, 4 colores)
    cpct_setVideoMode(1);

    // SOLUCIÓN: Usar la paleta definida anteriormente
    // Error: cpct_setPalette(palette, 16);
    // Correcto:
    cpct_setPalette(g_palette, 16);

    // Limpiar la pantalla
    // SOLUCIÓN: Usar casting explícito para direcciones de memoria
    cpct_memset((void *)SCREEN_START, 0, SCREEN_WIDTH * SCREEN_HEIGHT);

    // SOLUCIÓN: Crear un sprite usando nuestro pool en lugar de malloc
    // Error: Sprite* player = malloc(sizeof(Sprite));
    // Correcto:
    Sprite *player = allocate_sprite();
    if (player != NULL)
    {
        player->x = 40;
        player->y = 100;
        player->color = 1;
    }

    // Dibujar un rectángulo
    drawRectangle(10, 10, 20, 20, 1);

    // SOLUCIÓN: Usar paréntesis para expresiones con constantes hexadecimales
    // Error: cpct_drawSolidBox(0xC000 + 0x0100, 2, 30, 30);
    // Correcto:
    cpct_drawSolidBox((void *)(SCREEN_START + 0x0100), 2, 30, 30);

    // Bucle principal
    while (1)
    {
        // Escanear teclado
        cpct_scanKeyboard();

        // SOLUCIÓN: Usar variables definidas correctamente
        if (restart)
        {
            // Reiniciar juego
            restart = 0;
        }

        // Comprobar si se pulsa la tecla ESC
        if (cpct_isKeyPressed(Key_Esc))
        {
            break;
        }
    }
}

/**
 * Otros ejemplos de soluciones a errores comunes:
 *
 * 1. Error: array size missing
 *    Mal:  u8 my_array[];
 *    Bien: u8 my_array[10];
 *
 * 2. Error: incompatible types
 *    Mal:  u8* ptr = 0xC000;
 *    Bien: u8* ptr = (u8*)0xC000;
 *
 * 3. Error: indirections to different types assignment
 *    Mal:  void* generic_ptr = (void*)0xC000;
 *         Sprite* sprite_ptr = generic_ptr;
 *    Bien: void* generic_ptr = (void*)0xC000;
 *         Sprite* sprite_ptr = (Sprite*)generic_ptr;
 *
 * 4. Error: function does not take X arguments
 *    Verificar la documentación de CPCtelera para conocer los parámetros correctos
 *    Ejemplo correcto para cpct_drawSprite:
 *    cpct_drawSprite(sprite_data, (void*)0xC000, sprite_width, sprite_height);
 */