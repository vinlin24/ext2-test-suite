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


You can also see [my Piazza post](https://piazza.com/class/lcjl27z4agp66l/post/407).


### test_lab4_ext.py


**USAGE:**

```sh
python -m unittest # Run it with the handout unit test
./test_lab4_ext.py # Run this unit test alone
```

An extension of the handout test_lab4.py that gives a more comprehensive
coverage of the various stats of your mounted filesystem, like verifying file
modes, user IDs, file sizes, and of course file content. I tried to make this
more friendly towards incremental development by automatically skipping certain
tests if the necessary file(s) fails to mount.

`fsck.ext2` is great, but it also sometimes lets you get away with setting your data to something that's compliant with the ext2 standard but doesn't match the spec. Much of the tests here can also be verified by using `ls -ain mnt`, but this automates out the tediousness as well as gives you a better sanity check compared to the handout unit test every time you make a change.


### check_dump.py


**USAGE:**

```sh
./check_dump.py
```

This script compares the output of your:

```sh
dumpe2fs cs111-base.img
```

To the correct output example in the implementation guide provided by TA Can
Aygun in [this Piazza
upload](https://cdn-uploads.piazza.com/paste/k523wap3mgt7kn/32e5cbdc2f2ad85809c6e1b9eacecce7e333648952f1b16350d368bbe1f550ed/lab4_stages_F22.html).


<tr>
<th><center>With mismatches</center></th>
<th><center>All matching</center></th>
</tr>
<table>
<tr>
<td>

<!-- TODO: Add picture here. -->
</td>
<td>

<!-- TODO: Add picture here. -->
</td>
</tr>
</table>

Once again, just to take the error-prone tediousness out of eyeballing the comparisons every change. Notably, it also takes non-deterministic fields like the datetimes into consideration and gives nice color-coded formatting.


### dump_block.py


**USAGE:**

```sh
./dump_block.py --all dump.txt
./dump_block.py inode_bitmap --binary
./dump_block.py --help # See all available options
```

This script uses and formats the output of the [GNU
`xxd`](https://linux.die.net/man/1/xxd).

For more blunt or last-resort debugging, `(gdb) x/1024bx` on steroids. A script that dumps a specific block(s) within your 1 MiB cs111-base.img file in a more readable binary/hexadecimal format. This can probably be useful for checking whether you have garbage/incorrect initialized data in a block for some reason.

This also separates concerns by delegating data-dumping to an external debugging
script instead of having you write things like:

```c
static void dump_bitmap(u8 *bitmap)
{
    /* Am I even doing this right?  */
}
```

All over the place within your ext2-create.c source file.

**UPDATE:** I added the `--quiet` option which suppresses my custom format additions (only output what `xxd` does). This should let you be able to use this script in combination with coreutil text processing. For example:

```sh
# Count the number of cleared bits in your inode bitmap
./dump_block.py inode_bitmap --quiet -c 1 --binary | awk '{print $2}' | grep -o 0 | wc -l
```


## Contribution


We've got more than a week left for this lab! Feel free to open PRs with enhancements or your own scripts. We can make this a central script hub for Lab 4 👀.

Happy coding!
