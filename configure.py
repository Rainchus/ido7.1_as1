import os
import subprocess

dir_path = 'src/'
asm_path = 'asm/'
assets_path = 'assets/'
cflags = '-G 0 -fullwarn -verbose -Xcpluscomm -signed -nostdinc -non_shared -Wab,-r4300_mul'

header = (
    "AS = mips-linux-gnu-as\n"
    "CPP = cpp\n"
    "LD = mips-linux-gnu-ld\n"
    "OBJDUMP = mips-linux-gnu-objdump\n"
    "OBJCOPY = mips-linux-gnu-objcopy\n"
    "OBJCOPYFLAGS = -O binary\n"
    "PYTHON = python3\n"
    "cflags = -G 0 -fullwarn -verbose -Xcpluscomm -signed -nostdinc -non_shared -Wab,-r4300_mul\n"
    "include_cflags = -I. -Iinclude -Iinclude/PR -Iassets -Isrc\n"
    "check_warnings_gcc = -Wall -Waddress -Wextra -Wno-format-security -Wno-unknown-pragmas -Wno-unused-parameter -Wno-unused-variable -Wno-missing-braces -Wno-int-conversion -Wno-comment\n"
    "cc_check = gcc -fsyntax-only -fno-builtin -fsigned-char -std=gnu90 -m32 $check_warnings_gcc $include_cflags\n"
    "ido_cc = tools/ido_7.1/usr/lib/cc\n"
    "mips_version = -mips2\n"
    "DEFINES = -D_LANGUAGE_C -DF3DEX_GBI -DNDEBUG\n"
    "CFLAGS = -woff 649,838 $include_cflags\n"
    "ASM_PROC = python3 tools/asm-processor/build.py\n"
    "ASM_PROC_FLAGS = --input-enc=utf-8 --output-enc=euc-jp\n"
    "ASFLAGS = -EB -mtune=vr4300 -march=vr4300 -mabi=32 -Iinclude -Isrc\n"
    "OPTFLAGS = -O1\n"
    "objdump_command = $OBJDUMP $in > $in:.o=.s\n"
    "splat = python3 tools/splat/split.py as1.yaml\n"
    "XGCC = mips-linux-gnu-gcc\n"
    "MAKE_EXPECTED = tools/make_expected.py\n"
    "GCC_FLAGS = $include_cflags $DEFINES -G 0 -mno-shared -march=vr4300 -mfix4300 -mabi=32 -mhard-float -mdivide-breaks -fno-stack-protector -fno-common -fno-zero-initialized-in-bss -fno-PIC -mno-abicalls -fno-strict-aliasing -fno-inline-functions -ffreestanding -fwrapv -Wall -Wextra -Wno-missing-braces"
    "\n"

    "rule src_cc\n"
    "  command = $ASM_PROC $ASM_PROC_FLAGS $ido_cc -- $AS $ASFLAGS -- -c $cflags $DEFINES $CFLAGS $mips_version $OPTFLAGS -o $out $in\n"
    "\n"

    "rule s_file\n"
    "  command = iconv --from UTF-8 --to EUC-JP $in | $AS $ASFLAGS -o $out\n"
    "\n"

    "rule bin_file\n"
    "  command = $LD -r -b binary -o $out $in\n"
    "\n"

    "rule data_cc\n"
    " command = $XGCC -c $GCC_FLAGS -o $out $in\n"
    "\n"

    "rule make_elf\n"
    "  command = mips-linux-gnu-ld -T as1.ld -T undefined_syms_auto.txt -Map build/as1.map --no-check-sections -o $out\n"
    "\n"
)

# Traverse each subdirectory recursively and find all C files
def append_extension(filename):
    return filename + '.o'

c_files = []
for root, dirs, files in os.walk(dir_path):
    for file in files:
        if file.endswith('.c'):
            c_files.append(os.path.join(root, file))

s_files = []
for root, dirs, files in os.walk(asm_path):
    for file in files:
        if file.endswith('.s'):
            s_files.append(os.path.join(root, file))

bin_files = []
for root, dirs, files in os.walk(assets_path):
    for file in files:
        if file.endswith('.bin'):
            bin_files.append(os.path.join(root, file))

# Combine the lists and change file extensions
o_files = []
for file in c_files + s_files + bin_files:
    if 'asm/nonmatchings/' not in file:
        o_files.append("build/" + append_extension(file))

with open('build.ninja', 'w') as f:
    f.write(header)

# Write the full path of each C file to a new text file called build.ninja
with open('build.ninja', 'a') as outfile:
    # Write the rules for the .c files
    for c_file in c_files:
        folder_name = os.path.basename(os.path.dirname(c_file))
        outfile.write("build build/" + os.path.splitext(c_file)[0] + ".c.o: " + folder_name + "_cc " + c_file + "\n")

    # Write the rules for the .s files
    for s_file in s_files:
        if "asm/nonmatchings" in s_file:
            continue
        outfile.write("build build/" + os.path.splitext(s_file)[0] + ".s.o: " + "s_file " + s_file + "\n")

    # Write the rules for the .bin files
    for bin_file in bin_files:
        outfile.write("build build/" + os.path.splitext(bin_file)[0] + ".bin.o: " + "bin_file " + bin_file + "\n")


    # Build the ninja rule with the .o files
    outfile.write("build build/as1.elf: make_elf " + " ".join(o_files) + "\n")
