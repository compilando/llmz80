# LLMZ80 - Proyecto de Desarrollo para Z80

Este proyecto proporciona una estructura para desarrollar programas en ensamblador Z80 para microordenadores clásicos como el Amstrad CPC y el Sinclair ZX Spectrum.

## Requisitos Previos

### Herramientas de Desarrollo
- **SDCC (Small Device C Compiler)**: Compilador C para Z80
  ```bash
  # En Arch Linux:
  sudo pacman -S sdcc
  ```

- **CPCtelera**: Framework de desarrollo para Amstrad CPC
  ```bash
  # Clonar el repositorio
  git clone https://github.com/lronaldo/cpctelera.git
  cd cpctelera
  # Compilar e instalar
  make
  ```

- **Z88DK**: Herramientas de desarrollo para ZX Spectrum
  ```bash
  # En Arch Linux:
  sudo pacman -S z88dk
  ```

### Emuladores
- **Amstrad CPC**:
  - Caprice32 (recomendado)
    ```bash
    # En Arch Linux:
    sudo pacman -S caprice32
    ```
  - RetroVirtualMachine
  - XRoar

- **ZX Spectrum**:
  - Fuse (recomendado)
    ```bash
    # En Arch Linux:
    sudo pacman -S fuse
    ```
  - ZEsarUX
  - ZXSpin

## Estructura del Proyecto

```
llmz80/
├── examples/
│   ├── amstrad_cpc/          # Ejemplos para Amstrad CPC
│   │   ├── common/           # Archivos comunes
│   │   ├── easy/            # Ejemplos básicos
│   │   └── ...              # Otros ejemplos
│   └── spectrum/            # Ejemplos para ZX Spectrum
├── build_amstrad.sh         # Script de compilación para Amstrad
└── build_spectrum.sh        # Script de compilación para Spectrum
```

## Uso

### Compilación y Ejecución

#### Amstrad CPC
```bash
# Listar ejemplos disponibles
./build_amstrad.sh --list-examples

# Compilar y ejecutar un ejemplo
./build_amstrad.sh --example=text_example

# Compilar sin ejecutar el emulador
./build_amstrad.sh --example=text_example --no-emulator

# Especificar un emulador diferente
./build_amstrad.sh --example=text_example --emulator=cap32
```

#### ZX Spectrum
```bash
# Listar ejemplos disponibles
./build_spectrum.sh --list-examples

# Compilar y ejecutar un ejemplo
./build_spectrum.sh --example=text_example

# Compilar sin ejecutar el emulador
./build_spectrum.sh --example=text_example --no-emulator

# Especificar un emulador diferente
./build_spectrum.sh --example=text_example --emulator=fuse
```

### Creación de Nuevos Ejemplos

#### Amstrad CPC
```bash
# Crear estructura para un nuevo ejemplo
./build_amstrad.sh --create-example=mi_ejemplo
```

#### ZX Spectrum
```bash
# Crear estructura para un nuevo ejemplo
./build_spectrum.sh --create-example=mi_ejemplo
```

## Solución de Problemas

### Errores Comunes

1. **Error de compilación SDCC**:
   - Verificar que SDCC está instalado correctamente
   - Comprobar la versión de SDCC (recomendada: 4.2.0 o superior)

2. **Error de CPCtelera**:
   - Verificar que la ruta a CPCtelera es correcta en `build_amstrad.sh`
   - Asegurarse de que CPCtelera está compilado e instalado

3. **Error de Z88DK**:
   - Verificar que Z88DK está instalado correctamente
   - Comprobar que las variables de entorno están configuradas

4. **Error de emulador**:
   - Verificar que el emulador está instalado
   - Comprobar que el archivo DSK/TAP se genera correctamente

### Ver Soluciones Detalladas
```bash
# Para Amstrad CPC
./build_amstrad.sh --show-errors

# Para ZX Spectrum
./build_spectrum.sh --show-errors
```

## Configuración

### Ruta de CPCtelera
En `build_amstrad.sh`, ajusta la variable `CPCT_PATH` según tu instalación:
```bash
CPCT_PATH="/ruta/a/tu/cpctelera"
```

### Emulador por Defecto
Puedes cambiar el emulador por defecto en los scripts:
- Amstrad CPC: Variable `DEFAULT_EMULATOR` en `build_amstrad.sh`
- ZX Spectrum: Variable `DEFAULT_EMULATOR` en `build_spectrum.sh`

## Contribuir

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles. 