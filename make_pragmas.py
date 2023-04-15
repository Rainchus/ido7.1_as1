import os

directory = 'asm/nonmatchings'
for root, dirs, files in os.walk(directory):
    for filename in files:
        if filename.endswith('.s'):
            print('#pragma GLOBAL_ASM("{}")'.format(os.path.join(root, filename)))