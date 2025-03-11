##-----------------------------LICENSE NOTICE------------------------------------
##  This file is part of CPCtelera: An Amstrad CPC Game Engine 
##  Copyright (C) 2018 ronaldo / Fremos / Cheesetea / ByteRealms (@FranGallegoBR)
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU Lesser General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU Lesser General Public License for more details.
##
##  You should have received a copy of the GNU Lesser General Public License
##  along with this program.  If not, see <http://www.gnu.org/licenses/>.
##------------------------------------------------------------------------------
##
## PROJECT CONFIGURATION
##

# Name of the project (without spaces, as it will be used as filename)
PROJNAME   := anivemin

# Source files (.c, .s)
SRCFILES   := anivemin_example.c

# Location of the source files
SRCDIR     := .

# Output directory for compiled binaries and assets
OBJDIR     := obj

# Output directory for compiled binaries and assets
OBJDIR     := obj

# Compilation platform (linux, macos, win)
PLATFORM   := linux

# Compiler flags
Z80CCFLAGS := -mz80 --opt-code-size --std-c99

# Linker flags
Z80LDFLAGS := -mz80 --no-std-crt0 --code-loc 0x4000

# Executable file extension
EXTEXT     := bin

# Binary file extension
BINEXT     := bin

# Disk file extension
DSKEXT     := dsk

# Commands
MKDIR      := mkdir -p
RM         := rm -f
CP         := cp
ECHO       := echo

# Find CPCtelera directory
CPCT_PATH  := $(shell if [ -d "/home/oscar/cpctelera/cpctelera" ]; then echo "/home/oscar/cpctelera/cpctelera"; elif [ -d "$(CPCT_PATH)" ]; then echo "$(CPCT_PATH)"; else echo "CPCT_PATH not found"; fi)

# Memory location for Z80 code
Z80CODELOC := 0x4000

# Target binary file
TARGET     := $(PROJNAME).$(BINEXT)

# Target disk file
TARGETDSK  := $(PROJNAME).$(DSKEXT)

# Compilation flags
CCFLAGS    := $(Z80CCFLAGS) -I$(CPCT_PATH)/src
LDFLAGS    := $(Z80LDFLAGS) -L$(CPCT_PATH)/cpctelera.lib

# Object files
OBJFILES   := $(patsubst %.c,$(OBJDIR)/%.rel,$(notdir $(SRCFILES)))

# Default target
.PHONY: all clean

all: $(TARGETDSK)

# Create required directories
$(OBJDIR):
	$(MKDIR) $(OBJDIR)

# Compile .c files
$(OBJDIR)/%.rel: $(SRCDIR)/%.c | $(OBJDIR)
	$(CPCT_PATH)/tools/sdcc-3.6.8-r9946/bin/sdcc $(CCFLAGS) -c $< -o $@

# Link object files into a binary
$(TARGET): $(OBJFILES)
	$(CPCT_PATH)/tools/sdcc-3.6.8-r9946/bin/sdcc $(LDFLAGS) $(OBJFILES) -o $(TARGET)

# Create a DSK file
$(TARGETDSK): $(TARGET)
	$(CPCT_PATH)/tools/iDSK-0.13/bin/iDSK $(TARGETDSK) -n
	$(CPCT_PATH)/tools/iDSK-0.13/bin/iDSK $(TARGETDSK) -i $(TARGET) -t 1 -e 0x4000 -c 0x4000 -o 0

# Clean up generated files
clean:
	$(RM) -r $(OBJDIR)
	$(RM) $(TARGET)
	$(RM) $(TARGETDSK) 