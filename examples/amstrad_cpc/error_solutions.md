# Soluciones a Errores Comunes en el Desarrollo para Amstrad CPC

Este documento contiene soluciones a los errores más comunes que pueden surgir al desarrollar para Amstrad CPC usando CPCtelera y SDCC.

## Errores de Sintaxis

### Error: `syntax error: token -> 'u8'`

**Problema**: El compilador no reconoce el tipo de dato `u8`.

**Solución**: 
- Asegúrate de incluir `<cpctelera.h>` al principio de tu archivo.
- Este header define los tipos `u8`, `u16`, `u32`, etc.

```c
#include <cpctelera.h>

// Ahora puedes usar u8, u16, etc.
u8 myVariable = 42;
```

### Error: `syntax error: token -> '0x0400'`

**Problema**: SDCC puede tener problemas con algunas constantes hexadecimales, especialmente cuando se usan en expresiones complejas.

**Solución**:
- Usa paréntesis alrededor de las expresiones con constantes hexadecimales.
- Define constantes con nombres significativos.

```c
// Mal
cpct_drawSolidBox(0xC000 + 0x0400, 1, 40, 40);

// Bien - Usando paréntesis
cpct_drawSolidBox((void*)(0xC000 + 0x0400), 1, 40, 40);

// Mejor - Usando constantes definidas
#define SCREEN_START 0xC000
#define OFFSET_LINE_50 0x0400
cpct_drawSolidBox((void*)(SCREEN_START + OFFSET_LINE_50), 1, 40, 40);
```

### Error: `syntax error: token -> 'Node'`

**Problema**: El compilador no reconoce el tipo de estructura `Node`.

**Solución**:
- Asegúrate de definir la estructura antes de usarla.
- Verifica que la definición de la estructura sea correcta.
- Declara las variables del tipo de la estructura después de su definición.

## Errores de Variables

### Error: `Undefined identifier 'palette'`

**Problema**: Estás usando una variable que no ha sido definida.

**Solución**:
- Define todas las variables antes de usarlas.
- Para paletas, usa arrays de tamaño fijo.

```c
// Definición correcta de paleta
const u8 g_palette[16] = {0, 3, 6, 9, 12, 15, 18, 21, 24, 26, 28, 30, 31, 22, 14, 6};

// Ahora puedes usar g_palette
cpct_setPalette(g_palette, 16);
```

### Error: `Undefined identifier 'root'`

**Problema**: Estás usando una variable que no ha sido definida.

**Solución**:
- Declara la variable `root` antes de usarla.
- Si es una variable global, declárala al principio del archivo.
- Si es una variable local, declárala al principio de la función.

### Error: `Undefined identifier 'new_node'`

**Problema**: Estás usando una variable que no ha sido definida.

**Solución**:
- Declara la variable `new_node` antes de usarla.
- En funciones, declara todas las variables al principio de la función.

## Errores de Tipos

### Error: `converting integral to pointer without a cast`

**Problema**: Estás intentando usar un número como si fuera un puntero sin hacer un casting explícito.

**Solución**:
- Usa casting explícito cuando conviertas entre tipos, especialmente con punteros.

```c
// Mal
cpct_drawSolidBox(0xC000, 1, 40, 40);

// Bien
cpct_drawSolidBox((void*)0xC000, 1, 40, 40);
// o
cpct_drawSolidBox((u8*)0xC000, 1, 40, 40);
```

### Error: `incompatible types`

**Problema**: Estás intentando asignar un valor de un tipo a una variable de otro tipo incompatible.

**Solución**:
- Asegúrate de que los tipos coincidan en asignaciones y parámetros de funciones.
- Usa casting cuando sea necesario.

```c
// Mal
u8* ptr = 0xC000;

// Bien
u8* ptr = (u8*)0xC000;
```

### Error: `incompatible types from type 'void' to type 'signed-char generic* fixed'`

**Problema**: Estás intentando asignar un valor de un tipo a una variable de otro tipo incompatible.

**Solución**:
- Asegúrate de que los tipos sean compatibles.
- Usa casting explícito cuando sea necesario.

```c
// Mal
char* text = malloc(10);  // No hay malloc en Z80/CPCtelera

// Bien - Usando un array estático
char text_buffer[10];
char* text = text_buffer;

// O si necesitas asignar desde un puntero void
void* generic_ptr = (void*)0xC000;
char* text = (char*)generic_ptr;
```

### Error: `indirections to different types assignment`

**Problema**: Estás intentando asignar un puntero de un tipo a un puntero de otro tipo incompatible.

**Solución**:
- Asegúrate de que los tipos de punteros sean compatibles.
- Usa casting explícito cuando sea necesario.
- Verifica que estás usando el tipo correcto para las estructuras.

```c
// Mal
void* generic_ptr = malloc(10);
MyStruct* specific_ptr = generic_ptr;

// Bien
void* generic_ptr = malloc(10);
MyStruct* specific_ptr = (MyStruct*)generic_ptr;
```

### Error: `Pointer required`

**Problema**: Estás intentando usar el operador `->` con algo que no es un puntero.

**Solución**:
- Asegúrate de que la variable sea un puntero antes de usar `->`.
- Si la variable no es un puntero, usa el operador `.` en su lugar.
- Verifica que la variable esté correctamente inicializada.

## Errores de Arrays

### Error: `array size missing`

**Problema**: No has especificado el tamaño de un array.

**Solución**:
- Declara los arrays con tamaño fijo.

```c
// Mal
u8 my_array[];

// Bien
u8 my_array[10];
```

## Errores de Funciones

### Error: `function 'malloc' implicit declaration`

**Problema**: Estás usando una función que no ha sido declarada.

**Solución**:
- En CPCtelera/SDCC para Z80, **no hay malloc ni memoria dinámica**.
- Usa arrays estáticos en su lugar.
- Si necesitas estructuras de datos dinámicas, implementa tu propio gestor de memoria.

```c
// Mal - No hay malloc en Z80/CPCtelera
Node* new_node = malloc(sizeof(Node));

// Bien - Usa arrays estáticos
#define MAX_NODES 10
Node nodes_pool[MAX_NODES];
u8 next_free_node = 0;

// Función para "asignar" un nodo
Node* allocate_node() {
    if (next_free_node < MAX_NODES) {
        return &nodes_pool[next_free_node++];
    }
    return NULL; // No hay más nodos disponibles
}
```

### Error: `too many parameters`

**Problema**: Estás llamando a una función con más parámetros de los que acepta.

**Solución**:
- Verifica la firma correcta de la función.
- Consulta la documentación de CPCtelera para conocer los parámetros correctos.

```c
// Ejemplo correcto para cpct_drawSprite
cpct_drawSprite(sprite_data, (void*)0xC000, sprite_width, sprite_height);
```

## Estructuras de Datos Enlazadas

### Implementación de Listas Enlazadas

**Problema**: Intentar implementar listas enlazadas usando `malloc` y punteros como en C estándar.

**Solución**:
- Usa un array estático de nodos (pool) y un índice para el siguiente nodo libre.
- Implementa funciones para "asignar" y "liberar" nodos del pool.

```c
// Definición de la estructura Node
typedef struct Node {
    u8 value;
    struct Node* next;
} Node;

// Pool de nodos
#define MAX_NODES 20
Node nodes_pool[MAX_NODES];
u8 next_free_node = 0;

// Inicializar el pool
void init_nodes_pool() {
    next_free_node = 0;
    for (u8 i = 0; i < MAX_NODES; i++) {
        nodes_pool[i].value = 0;
        nodes_pool[i].next = NULL;
    }
}

// "Asignar" un nodo
Node* allocate_node() {
    if (next_free_node < MAX_NODES) {
        return &nodes_pool[next_free_node++];
    }
    return NULL;
}

// Ejemplo de uso para crear una lista enlazada
void create_linked_list() {
    // Inicializar el pool
    init_nodes_pool();
    
    // Crear el nodo raíz
    Node* root = allocate_node();
    if (root != NULL) {
        root->value = 10;
        
        // Añadir más nodos
        Node* current = root;
        for (u8 i = 1; i < 5; i++) {
            Node* new_node = allocate_node();
            if (new_node != NULL) {
                new_node->value = i * 10;
                current->next = new_node;
                current = new_node;
            }
        }
    }
}
```

### Implementación de Árboles

**Problema**: Intentar implementar árboles binarios u otras estructuras jerárquicas.

**Solución**:
- Usa el mismo enfoque de pool que para las listas enlazadas.
- Define la estructura con punteros a los nodos hijos.

```c
// Definición de un nodo de árbol binario
typedef struct TreeNode {
    u8 value;
    struct TreeNode* left;
    struct TreeNode* right;
} TreeNode;

// Pool de nodos de árbol
#define MAX_TREE_NODES 15
TreeNode tree_nodes_pool[MAX_TREE_NODES];
u8 next_free_tree_node = 0;

// Inicializar el pool
void init_tree_pool() {
    next_free_tree_node = 0;
    for (u8 i = 0; i < MAX_TREE_NODES; i++) {
        tree_nodes_pool[i].value = 0;
        tree_nodes_pool[i].left = NULL;
        tree_nodes_pool[i].right = NULL;
    }
}

// "Asignar" un nodo de árbol
TreeNode* allocate_tree_node() {
    if (next_free_tree_node < MAX_TREE_NODES) {
        return &tree_nodes_pool[next_free_tree_node++];
    }
    return NULL;
}

// Ejemplo de uso para crear un árbol binario simple
void create_binary_tree() {
    // Inicializar el pool
    init_tree_pool();
    
    // Crear el nodo raíz
    TreeNode* root = allocate_tree_node();
    if (root != NULL) {
        root->value = 50;
        
        // Crear nodos hijos
        TreeNode* left = allocate_tree_node();
        if (left != NULL) {
            left->value = 25;
            root->left = left;
        }
        
        TreeNode* right = allocate_tree_node();
        if (right != NULL) {
            right->value = 75;
            root->right = right;
        }
    }
}
```

## Ejemplo de Juego Anivemin (Adivinanza de Animal, Vegetal o Mineral)

**Problema**: Implementar un juego de adivinanzas con árboles de decisión.

**Solución**:
- Usa un árbol binario con un pool de nodos.
- Define claramente la estructura del nodo con los campos necesarios.
- Inicializa todas las variables antes de usarlas.

```c
#include <cpctelera.h>
#include <string.h>

// Definición de la estructura del nodo para el árbol de decisión
typedef struct Node {
    char question[40];           // Pregunta o respuesta
    struct Node* yes;            // Puntero al nodo si la respuesta es "sí"
    struct Node* no;             // Puntero al nodo si la respuesta es "no"
    u8 is_answer;                // 1 si es una respuesta final, 0 si es una pregunta
} Node;

// Pool de nodos para simular memoria dinámica
#define MAX_NODES 30
Node nodes_pool[MAX_NODES];
u8 next_free_node = 0;

// Variables globales para las categorías
Node* animal = NULL;
Node* vegetal = NULL;
Node* mineral = NULL;
Node* current_node = NULL;

// Inicializar el pool de nodos
void init_nodes_pool() {
    next_free_node = 0;
    for (u8 i = 0; i < MAX_NODES; i++) {
        nodes_pool[i].question[0] = '\0';
        nodes_pool[i].yes = NULL;
        nodes_pool[i].no = NULL;
        nodes_pool[i].is_answer = 0;
    }
}

// "Asignar" un nodo del pool
Node* allocate_node() {
    if (next_free_node < MAX_NODES) {
        return &nodes_pool[next_free_node++];
    }
    return NULL;
}

// Inicializar el árbol de decisión
void init_decision_tree() {
    // Inicializar el pool
    init_nodes_pool();
    
    // Crear nodos para las categorías principales
    animal = allocate_node();
    vegetal = allocate_node();
    mineral = allocate_node();
    
    // Configurar nodos de categorías
    if (animal) {
        strcpy(animal->question, "Es un perro?");
        animal->is_answer = 1;
    }
    
    if (vegetal) {
        strcpy(vegetal->question, "Es un arbol?");
        vegetal->is_answer = 1;
    }
    
    if (mineral) {
        strcpy(mineral->question, "Es una piedra?");
        mineral->is_answer = 1;
    }
    
    // Conectar los nodos
    if (animal && vegetal) {
        animal->no = vegetal;
    }
}

void main(void) {
    // Variables locales
    char response[20];
    
    // Desactivar firmware
    cpct_disableFirmware();
    
    // Establecer modo de vídeo
    cpct_setVideoMode(1);
    
    // Inicializar el árbol de decisión
    init_decision_tree();
    
    // Establecer el nodo actual
    current_node = animal;
    
    // Bucle principal
    while(1) {
        // Escanear teclado
        cpct_scanKeyboard();
        
        // Comprobar si se pulsa la tecla ESC
        if (cpct_isKeyPressed(Key_Esc)) {
            break;
        }
    }
}
```

## Ejemplo Completo Correcto

```c
#include <cpctelera.h>

// Definición correcta de constantes
#define SCREEN_START 0xC000
#define OFFSET_LINE_50 0x0400

// Definición correcta de paleta
const u8 g_palette[16] = {0, 3, 6, 9, 12, 15, 18, 21, 24, 26, 28, 30, 31, 22, 14, 6};

// Definición correcta de una estructura
typedef struct {
    u8 x;
    u8 y;
    u8 color;
} Sprite;

// Pool de sprites para simular memoria dinámica
#define MAX_SPRITES 10
Sprite sprites_pool[MAX_SPRITES];
u8 next_free_sprite = 0;

// Función para "asignar" un sprite
Sprite* allocate_sprite() {
    if (next_free_sprite < MAX_SPRITES) {
        return &sprites_pool[next_free_sprite++];
    }
    return NULL; // No hay más sprites disponibles
}

void main(void) {
    // Desactivar firmware
    cpct_disableFirmware();
    
    // Establecer modo de vídeo (1 = 320x200, 4 colores)
    cpct_setVideoMode(1);
    
    // Establecer paleta de colores
    cpct_setPalette(g_palette, 16);
    
    // Crear un sprite usando nuestro pool
    Sprite* player = allocate_sprite();
    if (player != NULL) {
        player->x = 40;
        player->y = 100;
        player->color = 1;
    }
    
    // Dibujar un rectángulo sólido (con casting correcto)
    cpct_drawSolidBox((void*)SCREEN_START, 1, 40, 40);
    
    // Bucle principal
    while(1) {
        // Escanear teclado
        cpct_scanKeyboard();
        
        // Comprobar si se pulsa la tecla ESC
        if (cpct_isKeyPressed(Key_Esc)) {
            break;
        }
    }
}
```

## Errores de Enlazado

### Error: `Undefined Global '_cpct_setPalette' referenced by module`

**Problema**: El enlazador no puede encontrar la función `cpct_setPalette` en las librerías.

**Solución**:
- Asegúrate de incluir la librería de CPCtelera correctamente en el Makefile.
- Añade `$(CPCT_PATH)/cpctelera.lib` al comando de enlazado.
- Verifica que la ruta a CPCtelera sea correcta.

## Errores de Herramientas

### Error: `Trop d'options !` (iDSK)

**Problema**: La herramienta iDSK está recibiendo demasiadas opciones o opciones incorrectas.

**Solución**:
- Simplifica el comando iDSK.
- Elimina la opción `-o 0` si no es necesaria.
- Usa `4000` en lugar de `0x4000` para las direcciones.

## Ejemplos de Soluciones

### Declaración de Variables Globales

```c
// Definición de la estructura
typedef struct Node {
    char question[40];
    struct Node *yes;
    struct Node *no;
    u8 is_answer;
    u8 category;
} Node;

// Variables globales
Node *root = NULL;
Node *current_node = NULL;
```

### Declaración de Variables Locales

```c
void process_input() {
    // Declarar variables al inicio de la función
    Node *new_node;
    
    // Resto de la función
    // ...
    
    // Usar la variable
    new_node = allocate_node();
}
```

### Makefile Correcto para CPCtelera

```makefile
# Link object files into a binary
$(TARGET): $(OBJFILES)
	$(CPCT_PATH)/tools/sdcc-3.6.8-r9946/bin/sdcc $(LDFLAGS) $(OBJFILES) -o $(TARGET) $(CPCT_PATH)/cpctelera.lib

# Create a DSK file
$(TARGETDSK): $(TARGET)
	$(CPCT_PATH)/tools/iDSK-0.13/bin/iDSK $(TARGETDSK) -n
	$(CPCT_PATH)/tools/iDSK-0.13/bin/iDSK $(TARGETDSK) -i $(TARGET) -t 1 -e 4000 -c 4000
```

## Ejemplo Completo: Anivemin

Para ver un ejemplo completo de un juego que implementa un árbol de decisión sin usar memoria dinámica, consulta el ejemplo `anivemin_example` en la carpeta `examples/amstrad_cpc/anivemin_example`.

Puedes compilarlo con:

```bash
./build_amstrad.sh --example=anivemin_example
```

## Recursos Adicionales

- [Documentación oficial de CPCtelera](https://lronaldo.github.io/cpctelera/)
- [Wiki de CPCtelera](https://github.com/lronaldo/cpctelera/wiki)
- [Foro de CPCtelera](https://github.com/lronaldo/cpctelera/discussions) 