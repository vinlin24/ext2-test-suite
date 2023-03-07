ifeq ($(shell uname -s),Darwin)
	CFLAGS = -std=gnu17 -pthread -Wall -O0 -pipe -fno-plt -fPIC
	LDFLAGS =
else
	CFLAGS = -std=gnu17 -pthread -Wall -O0 -pipe -fno-plt -fPIC
	LDFLAGS = -lrt -pthread -Wl,-O1,--sort-common,--as-needed,-z,relro,-z,now
endif

.PHONY: all
all: ext2-create

##### Building My Lab Implementation #####

ext2-create: ext2-create.o

.PHONY: clean
clean:
	rm -f ext2-create.o ext2-create
	rm -f *.img
	rm -f *.tar
	rm -rf __pycache__

##### Workflow Commands #####

# Create the filesystem image from the compiled program.
.PHONY: img
img: cs111-base.img
cs111-base.img: ext2-create
	./ext2-create

# Dump filesystem information to help debugging.
.PHONY: dump
dump: cs111-base.img
	dumpe2fs cs111-base.img

# Check the filesystem for correctness.
.PHONY: check
check: cs111-base.img
	fsck.ext2 cs111-base.img

# Mount the filesystem to a temporary directory.
.PHONY: mount
mount: mnt
mnt: cs111-base.img
	-mkdir mnt
	sudo mount -o loop cs111-base.img mnt

# Unmount the filesystem and clean up the temporary directory.
.PHONY: unmount
unmount:
	-sudo umount mnt
	-rmdir mnt

##### Test Suite Distribution #####

SUITE_FILES = check_dump.py test_lab4_ext.py dump_block.py

.PHONY: suite
suite: lab4-test-suite.tar
lab4-test-suite.tar: $(SUITE_FILES)
	tar -cf $@ $^
