# Lab 4 ext2 Test Suite


A collection of useful scripts for your debugging and testing workflow for the **W23 COM SCI 111 Lab 4: Hey! I'm Filing Here.**


## Setup


This suite has been outfitted with a [setup script](setup.sh) to automate its integration into your lab directory. First clone this repository into some directory outside your lab directory and run the script:

```sh
mkdir lab4-test-suite
git clone https://github.com/vinlin24/ext2-test-suite.git lab4-test-suite
cd lab4-test-suite
./setup.sh /path/to/lab4 # Specify your lab directory here
```

This will untar my scripts into your lab directory as well as append their patterns to your `.gitignore` such that they don't clutter your version control.

If this repository updates between now and the due date, you can simply pull in `lab4-test-suite` and run the setup again.


## Scripts


You can also see [my Piazza post](https://piazza.com/class/lcjl27z4agp66l/post/407) for alternative descriptions of these scripts as well as images of their demo.


### test_lab4_ext.py


**USAGE:**

```sh
python -m unittest # Run it with the handout unit test
./test_lab4_ext.py # Run this unit test alone
```

An extended version of the `test_lab4.py` unit tester handout. Pretty self-explanatory. This tester checkes the *characteristics* (stats) of your mounted filesystem, if possible. I tried to make this more friendly towards incremental development by automatically skipping certain tests if the necessary file(s) fails to mount.

Most of these tests can be verified by eyeballing the output of:

```sh
ls -ain mnt
```

This script just takes the tediousness out of it.


### check_dump.py


**USAGE:**

```sh
./check_dump.py
```

This script compares the output of your:

```sh
dumpe2fs cs111-base.img
```

To the correct output example in the implementation guide provided by TA Can Aygun in [this Piazza upload](https://cdn-uploads.piazza.com/paste/k523wap3mgt7kn/32e5cbdc2f2ad85809c6e1b9eacecce7e333648952f1b16350d368bbe1f550ed/lab4_stages_F22.html).

This script takes the tediousness out of manually comparing your `dumpe2fs` output every time you make a change.


### dump_block.py


**USAGE:**

```sh
./dump_block.py --all dump.txt
./dump_block.py inode_bitmap --binary
./dump_block.py --help # See all available options
```

For more blunt or last-resort debugging, this script uses and formats the output of the [GNU `xxd`](https://linux.die.net/man/1/xxd) command to dump the binary data of the specified block within your 1 MiB cs111-base.img file.

Probably just useful to see if you have garbage at a block for some reason to be honest. Theoretically you could "check for a specific `struct` field", which I was really excited to implement but realized that required people to be desperate enough to count with fingers and do `struct` offset arithmetic. GDB is faster lol.

Might make this a bit more usable if I can be bothered to.

**UPDATE:** I added the `--quiet` option which suppresses my custom format additions (only output what `xxd` does). This should let you be able to use this script in combination with coreutil text processing. For example:

```sh
# Count the number of cleared bits in your inode bitmap
./dump_block.py inode_bitmap --quiet -c 1 --binary | awk '{print $2}' | grep -o 0 | wc -l
```


## Contribution


We've got more than a week left for this lab! Feel free to open PRs with enhancements or your own scripts. We can make this a central script hub for Lab 4 👀.

Happy coding!
