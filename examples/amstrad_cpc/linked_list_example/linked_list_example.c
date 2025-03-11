/**
 * @file linked_list_example.c
 * @brief Ejemplo de implementación de listas enlazadas en Amstrad CPC
 *
 * Este ejemplo muestra cómo implementar listas enlazadas en Amstrad CPC
 * sin usar malloc, utilizando un pool de nodos preasignados.
 */

#include <cpctelera.h>

// Definición de la estructura Node para la lista enlazada
typedef struct Node
{
    u8 value;          // Valor almacenado en el nodo
    struct Node *next; // Puntero al siguiente nodo
} Node;

// Pool de nodos para simular memoria dinámica
#define MAX_NODES 20
Node nodes_pool[MAX_NODES];
u8 next_free_node = 0;

// Paleta de colores
const u8 g_palette[16] = {
    0, 3, 6, 9, 12, 15, 18, 21,
    24, 26, 28, 30, 31, 22, 14, 6};

/**
 * @brief Inicializa el pool de nodos
 */
void init_nodes_pool()
{
    next_free_node = 0;
    for (u8 i = 0; i < MAX_NODES; i++)
    {
        nodes_pool[i].value = 0;
        nodes_pool[i].next = NULL;
    }
}

/**
 * @brief "Asigna" un nodo del pool
 * @return Puntero al nodo asignado o NULL si no hay nodos disponibles
 */
Node *allocate_node()
{
    if (next_free_node < MAX_NODES)
    {
        return &nodes_pool[next_free_node++];
    }
    return NULL; // No hay más nodos disponibles
}

/**
 * @brief Crea una lista enlazada con valores secuenciales
 * @param count Número de nodos a crear
 * @return Puntero al primer nodo de la lista
 */
Node *create_list(u8 count)
{
    if (count == 0 || count > MAX_NODES)
    {
        return NULL;
    }

    // Crear el nodo raíz
    Node *root = allocate_node();
    if (root == NULL)
    {
        return NULL;
    }

    root->value = 1;

    // Añadir el resto de nodos
    Node *current = root;
    for (u8 i = 2; i <= count; i++)
    {
        Node *new_node = allocate_node();
        if (new_node == NULL)
        {
            break; // No hay más nodos disponibles
        }

        new_node->value = i;
        current->next = new_node;
        current = new_node;
    }

    return root;
}

/**
 * @brief Dibuja la lista enlazada en pantalla
 * @param list Puntero al primer nodo de la lista
 */
void draw_list(Node *list)
{
    u8 x = 10;
    u8 y = 80;

    // Dibujar cada nodo
    Node *current = list;
    while (current != NULL)
    {
        // Dibujar un rectángulo para representar el nodo
        cpct_drawSolidBox((void *)(0xC000 + y * 80 + x), current->value % 4 + 1, 20, 20);

        // Dibujar una línea para representar el enlace
        if (current->next != NULL)
        {
            for (u8 i = 0; i < 10; i++)
            {
                cpct_drawPixel((void *)(0xC000 + y * 80 + x + 20 + i), 3);
            }
        }

        // Avanzar a la siguiente posición
        x += 30;
        current = current->next;
    }
}

/**
 * @brief Función principal
 */
void main(void)
{
    // Desactivar firmware
    cpct_disableFirmware();

    // Establecer modo de vídeo (1 = 320x200, 4 colores)
    cpct_setVideoMode(1);

    // Establecer paleta de colores
    cpct_setPalette(g_palette, 16);

    // Limpiar la pantalla
    cpct_memset((void *)0xC000, 0, 0x4000);

    // Inicializar el pool de nodos
    init_nodes_pool();

    // Crear una lista enlazada con 5 nodos
    Node *list = create_list(5);

    // Dibujar la lista
    draw_list(list);

    // Bucle principal
    while (1)
    {
        // Escanear teclado
        cpct_scanKeyboard();

        // Comprobar si se pulsa la tecla ESC
        if (cpct_isKeyPressed(Key_Esc))
        {
            break;
        }
    }
}