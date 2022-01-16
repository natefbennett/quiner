# Author:    Nate Bennett
# Date:      1/16/22
# File:      quiner.py
# License:   MIT
#
# This python script to gives a basic C program the ability to self reproduce! 

import sys
import re

# take in an iterable of bytes and output a string
# returned string is a valid C style array of bytes
def CStyleByteArray(byte_list):
    
    byte_array = 'const unsigned char data[] = {'
    
    for i, hex_val in enumerate(byte_list):
        if i % 8 == 0 and i != 0:
            byte_array += f'\n{hex(hex_val)}, '
        else:
            byte_array += f'{hex(hex_val)}, '

    byte_array += '};\n'

    return byte_array


# open input file and read into string
f = open(sys.argv[1])
c_src = f.read()
f.close()

# quine section to inject into c program
c_quine_section = \
'''
printf ("const unsigned char data[] = {");

unsigned int i;
for ( i=0 ; i<sizeof(data) ; i++ ) {
    if ( i%8 == 0 ) {
        printf ("\\n/* %0#6x */",i);
    }
    printf ("  %0#4x,", data[i]);
}
    
printf ("\\n};\\n\\n");
for ( i=0 ; i<sizeof(data) ; i++ ) {
    putchar (data[i]);
}
'''
# new main() components to inject
c_new_if = 'main( int argc, char *argv[] ){\nif ( argc == 2 && *argv[1] == \'q\') {'
c_new_else = '} else {'
c_new_end = 'return 0;\n}\n}'

# extract useful parts of c program
# inject some of the new code
c_new_src = re.sub( 'main[ \t\n]*\(.*\)[ \t\n]*{', c_new_if, c_src )
c_src_in_main = re.search( re.escape(c_new_if)+'([\s\S]*)}[ \t\n]*$', c_new_src ).group(1)

# piece together new main function
c_new_in_main = f'''
        {repr(c_quine_section).strip("'")}
    }} else {{
        {repr(c_src_in_main).strip("'")}
    }}
    return 0;
'''

# inject new main() function into program
c_new_src = re.sub( re.escape(c_src_in_main), c_new_in_main, c_new_src )

# get byte representation of new quine program
c_byte_array = CStyleByteArray(bytearray(c_new_src.encode())) + '\n'

# append c style byte array to top of file and print to stdout
print(c_byte_array + c_new_src)
