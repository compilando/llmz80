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
PROJNAME   := error_solutions

# Folders and CPCtelera location
SRCDIR     := .
OBJDIR     := obj
DSKDIR     := dsk
BINDIR     := bin

# Find CPCtelera path
ifndef CPCT_PATH
CPCT_PATH := $(shell if [ -d "$(HOME)/cpctelera/cpctelera" ]; then echo "$(HOME)/cpctelera/cpctelera"; \
             elif [ -d "/opt/cpctelera/cpctelera" ]; then echo "/opt/cpctelera/cpctelera"; \
             elif [ -d "/usr/local/cpctelera/cpctelera" ]; then echo "/usr/local/cpctelera/cpctelera"; \
             elif [ -d "/usr/share/cpctelera/cpctelera" ]; then echo "/usr/share/cpctelera/cpctelera"; \
             else echo ""; fi)
endif

# Z80 Memory location where code will start in memory
Z80CODELOC := 0x4000

# Automatically calculated variables
TARGET     := $(PROJNAME).bin
DSK        := $(PROJNAME).dsk

# Compilation flags
CFLAGS     := -mz80 -Wall -Werror -Wno-unused-parameter -Wno-incompatible-pointer-types
CFLAGS     += -I$(CPCT_PATH)/src
CFLAGS     += -I$(CPCT_PATH)/src/strings
CFLAGS     += -I$(CPCT_PATH)/src/video
CFLAGS     += -I$(CPCT_PATH)/src/audio
CFLAGS     += -I$(CPCT_PATH)/src/input
LDFLAGS    := -mz80 -Wl,-Ttext=$(Z80CODELOC) -Wl,--no-check-sections
LDFLAGS    += -L$(CPCT_PATH)/cpctelera.lib
LDLIBS     := -lcpctelera

# Source files and object files
SRCS       := $(wildcard $(SRCDIR)/*.c)
OBJS       := $(patsubst $(SRCDIR)/%.c,$(OBJDIR)/%.rel,$(SRCS))

# Default target: build the DSK file
.PHONY: all clean

all: $(DSK)

# Create required folders
$(OBJDIR) $(BINDIR) $(DSKDIR):
	@mkdir -p $@

# Compile .c files into .rel object files
$(OBJDIR)/%.rel: $(SRCDIR)/%.c | $(OBJDIR)
	@echo "Compiling $<"
	@sdcc $(CFLAGS) -c $< -o $@

# Link all object files into a .bin file
$(BINDIR)/$(TARGET): $(OBJS) | $(BINDIR)
	@echo "Linking $@"
	@sdcc $(LDFLAGS) $(OBJS) $(LDLIBS) -o $(BINDIR)/$(PROJNAME).ihx
	@hex2bin -e bin $(BINDIR)/$(PROJNAME).ihx
	@mv $(BINDIR)/$(PROJNAME).bin $@

# Create DSK file with the binary
$(DSK): $(BINDIR)/$(TARGET) | $(DSKDIR)
	@echo "Creating DSK file $@"
	@$(CPCT_PATH)/tools/iDSK/iDSK $@ -n
	@$(CPCT_PATH)/tools/iDSK/iDSK $@ -i $(BINDIR)/$(TARGET) -t bin -e 0x4000 -c 0x4000 -l 0x4000
	@echo "Done!"

# Clean all generated files
clean:
	@echo "Cleaning project..."
	@rm -rf $(OBJDIR) $(BINDIR) $(DSKDIR) $(DSK)
	@echo "Done!" 