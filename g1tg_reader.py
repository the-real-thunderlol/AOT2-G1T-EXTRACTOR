import struct
from convert_raw_image_data import save_as_dds

show_verbose = True

def show_data(data):
    hex_str = " ".join(f"{b:02x}" for b in data)
    ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in data)
    print(f"{hex_str}  |  {ascii_str}")

with open("chunk_11820.g1t", "rb") as file: # from the BIN file extractor
    bytes_given = 28

    for start in range(0,1):

        magic = file.read(4)
        version = file.read(4)
        print(f"        Magic Bytes: {magic}"   )
        print(f"           Version : {version}" )


        data = file.read(20) # read header


        # convert 20 bytes to little endian
        little_endian_data = struct.unpack("<IIIII", data[:bytes_given])
        total_size, header_offset, total_texures, unknown, pad1 = little_endian_data
        print(f"Total size in bytes: {total_size}"    )
        print(f"            Entries: {header_offset}" )
        print(f"              Files: {total_texures}" )
        print(f" Something not used: {unknown}"           )


#################################################################################
    texture_number = 1
    # texture_raw = []
    n = 0
    # store raw types
    for x in range(0,total_texures):
        data = file.read(4)
        # texture_raw.append(data)

        ### not really used anywhere other than internally to define what kind of texture each file is
        if show_verbose == True:
            if data == b'\x00\x00\x00\x00':
                print(f"\nTexture {texture_number}")
                print(f"{n} - Texture: ", end="")
                texture_number = texture_number + 1
            elif data == b'\x03\x00\x00\x00':
                print(f"{n} - Normal: ", end="")
            elif data == b'\x02\x00\x00\x00':
                print(f"{n} - Mipmap: ", end="")
            elif data == b'\x04\x00\x00\x00':
                print(f"{n} - Noise: ", end="")
            else:
                print("---STOP---")
                exit(1)

            n = n + 1
            show_data(data)


#############################################################################

    ### GET OFFSETS OF FILES
    offsets = []
    raw_types_table_size = total_texures * 4
    #print(raw_types_table_size)

    for y in range (0,total_texures):
        data = file.read(4)
        # convert to little endian
        little_endian_data = struct.unpack("<I", data)[0]


        ### add 28 bytes for header and table 1 byte size to little endian to get relativfe position
        little_endian_data = little_endian_data + raw_types_table_size + 28
        offsets.append(little_endian_data)

#########################################################################

    # extract files
    for z in range (0, total_texures): #total_texures
        file.seek(offsets[z])
        data = file.read(8)

        mipmap_byte, texture, dimension, flag0, flag1, flag2, flag3, flag4 = struct.unpack("<BBBBBBBB", data)[:8]
        # get last 4 bits
        right_mipmaps = mipmap_byte & 0x0F #16 -> last 4 by using and operator with 1111
        dimension_right = dimension & 0x0F

        # get the first 4 bits
        left_mipmap = mipmap_byte >> 4
        dimension_left = dimension >> 4

        width = 2 ** dimension_right
        height = 2 ** dimension_left

        data = file.read(12) ## 12 0 0 , 12 0 16777216; 16777216 => 1 in Big Endian
        size = struct.unpack("<III", data)
        is_srgb = False
        if size[2] == 16777216:
            is_srgb = True

        print(f"{z}: {size}")

        # go back to start of file
        file.seek(offsets[z])
        if z < total_texures - 1:
            texture_size = offsets[z+1] - offsets[z]
        else:
            texture_size = total_size - offsets[z]

        texture_data = file.read(texture_size)



        skip = 20 # skip 20 bytes (header)
        save_as_dds(texture_data[skip:], width, height, texture, left_mipmap, is_srgb,  f"out/texture_{z}.dds")