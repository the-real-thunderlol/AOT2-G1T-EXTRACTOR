"""
Generated via claude code.
Just add the 124 bytes of main header data, replacing the raw texture data recieved.
"""

import struct

# DDS header constants
DDS_MAGIC = b'DDS '

# DDS flags
DDSD_CAPS = 0x1
DDSD_HEIGHT = 0x2
DDSD_WIDTH = 0x4
DDSD_LINEARSIZE = 0x80000
DDSD_PIXELFORMAT = 0x1000
DDSD_MIPMAPCOUNT = 0x20000

# Pixel format flags
DDPF_FOURCC = 0x4

# Caps
DDSCAPS_TEXTURE = 0x1000
DDSCAPS_MIPMAP = 0x400000
DDSCAPS_COMPLEX = 0x8

# G1T texture type to DDS format mapping
# type byte -> (fourcc, block_size, bits_per_pixel)

#test and trial here. checked which worked for what file based on their format
g1t_format_map = {
    0x06: (b'DXT1',  8, 4),     # BC1
    0x08: (b'DXT5', 16, 8),    # BC3
    0x09: (b'ATI1',  8, 4),     # BC4
    0x0A: (b'ATI2', 16, 8),    # BC5
    0x10: (b'DXT1',  8, 4),     # BC1
    0x12: (b'DXT5', 16, 8),    # BC3


    0x59: (b'DXT1',  8, 4),     # BC1
    0x5B: (b'DXT5', 16, 8),    # BC3
}

# DXGI formats for DX10 header
DXGI_FORMAT_BC1_UNORM = 71
DXGI_FORMAT_BC1_UNORM_SRGB = 72
DXGI_FORMAT_BC3_UNORM = 77
DXGI_FORMAT_BC3_UNORM_SRGB = 78
DXGI_FORMAT_BC7_UNORM = 98
DXGI_FORMAT_BC7_UNORM_SRGB = 99

# maps G1T type to (linear DXGI, sRGB DXGI)
g1t_srgb_map = {
    0x06: (DXGI_FORMAT_BC1_UNORM, DXGI_FORMAT_BC1_UNORM_SRGB),
    0x10: (DXGI_FORMAT_BC1_UNORM, DXGI_FORMAT_BC1_UNORM_SRGB),
    0x59: (DXGI_FORMAT_BC1_UNORM, DXGI_FORMAT_BC1_UNORM_SRGB),
    0x08: (DXGI_FORMAT_BC3_UNORM, DXGI_FORMAT_BC3_UNORM_SRGB),
    0x12: (DXGI_FORMAT_BC3_UNORM, DXGI_FORMAT_BC3_UNORM_SRGB),
    0x5B: (DXGI_FORMAT_BC3_UNORM, DXGI_FORMAT_BC3_UNORM_SRGB),
}


def build_dds_header(width, height, texture_type, mipmaps, is_srgb=False):
    if texture_type not in g1t_format_map:
        print(f"Unknown texture type: {texture_type}")
        return None

    fourcc, block_size, bpp = g1t_format_map[texture_type]

    # calculate linear size
    linear_size = max(1, (width + 3) // 4) * max(1, (height + 3) // 4) * block_size

    # flags
    flags = DDSD_CAPS | DDSD_HEIGHT | DDSD_WIDTH | DDSD_PIXELFORMAT | DDSD_LINEARSIZE
    caps = DDSCAPS_TEXTURE

    if mipmaps > 1:
        flags |= DDSD_MIPMAPCOUNT
        caps |= DDSCAPS_MIPMAP | DDSCAPS_COMPLEX

    # pixel format (32 bytes)
    pixel_format = struct.pack("<IIII IIII",
        32,             # dwSize
        DDPF_FOURCC,    # dwFlags
        struct.unpack("<I", fourcc)[0],  # dwFourCC
        0,              # dwRGBBitCount
        0, 0, 0, 0     # bit masks
    )

    # reserved (11 ints = 44 bytes)
    reserved = b'\x00' * 44

    # main header (124 bytes)
    header = struct.pack("<III III I",
        124,            # dwSize
        flags,          # dwFlags
        height,         # dwHeight
        width,          # dwWidth
        linear_size,    # dwPitchOrLinearSize
        0,              # dwDepth
        mipmaps,        # dwMipMapCount
    )
    header += reserved
    header += pixel_format
    header += struct.pack("<IIIII",
        caps,           # dwCaps
        0,              # dwCaps2
        0, 0, 0        # dwCaps3, dwCaps4, dwReserved2
    )

    # if sRGB, override fourcc to use DX10 header
    if is_srgb and texture_type in g1t_srgb_map:
        fourcc = b'DX10'
        pixel_format = struct.pack("<IIII IIII",
            32,             # dwSize
            DDPF_FOURCC,    # dwFlags
            struct.unpack("<I", fourcc)[0],  # dwFourCC
            0,              # dwRGBBitCount
            0, 0, 0, 0     # bit masks
        )
        # rebuild header with DX10 fourcc
        header = struct.pack("<III III I",
            124, flags, height, width, linear_size, 0, mipmaps,
        )
        header += reserved
        header += pixel_format
        header += struct.pack("<IIIII", caps, 0, 0, 0, 0)

    result = DDS_MAGIC + header

    # add DX10 extended header
    if fourcc == b'DX10':
        if texture_type in g1t_srgb_map:
            linear_fmt, srgb_fmt = g1t_srgb_map[texture_type]
            dxgi_format = srgb_fmt if is_srgb else linear_fmt
        elif texture_type == 0x5B:
            dxgi_format = DXGI_FORMAT_BC7_UNORM_SRGB
        else:
            dxgi_format = DXGI_FORMAT_BC7_UNORM

        dx10_header = struct.pack("<IIIII",
            dxgi_format,    # dxgiFormat
            3,              # resourceDimension (D3D10_RESOURCE_DIMENSION_TEXTURE2D)
            0,              # miscFlag
            1,              # arraySize
            0               # miscFlags2
        )
        result += dx10_header

    return result


def save_as_dds(pixel_data, width, height, texture_type, mipmaps, is_srgb, output_path):
    header = build_dds_header(width, height, texture_type, mipmaps, is_srgb)
    if header is None:
        return False

    with open(output_path, "wb") as out:
        out.write(header)
        out.write(pixel_data)

    return True
