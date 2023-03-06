SUITE_FILES = check_dump.py test_lab4_ext.py dump_block.py dump_example.txt

.PHONY: all

all: lab4-test-suite.tar

lab4-test-suite.tar: $(SUITE_FILES)
	tar -cf $@ $^
