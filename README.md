Attack on Titan 2 Modding: G1T Extractor

## REQUIRES USAGE OF [LINKDATA-EXTRACTOR](https://github.com/the-real-thunderlol/AOT2-LINKDATA-EXTRACTOR) IN ORDER TO EXTRACT G1T files.

Link: <a href="https://github.com/the-real-thunderlol/AOT2-LINKDATA-EXTRACTOR">https://github.com/the-real-thunderlol/AOT2-LINKDATA-EXTRACTOR</a>

AOT2 Discord: https://discord.gg/fytRnTNTuP

===

## **FINDINGS:**
- Little endian is used
little_endian_data = struct.unpack("<III", data[:12])
print(little_endian_data)

---

magic, version, total_size, header_offset, total_texures, unknown, pad1 = little_endian_data

## Header: ( 28 bytes ) {basically 4 bytes per line}

row 1 - G1TG (47 54 31 47)
row 2 - 1600 (31 36 30 30) - version 16
row 3 - total size
row 4 - Texture Header Offset {for LINKDATA_A/11819.g1t its 4740 {plus 12 bytes from header}}
row 5 - Texture count
row 6 - platform version (10 for PC)
row 7 - padding 1

## **Table 1: ( 4 bytes ):**

 Pattern defining what kind of texture.

00 00 00 00  |  ->  texture
03 00 00 00  |  -> normal map (purple blue texture)
02 00 00 00  |  -> mipmap/metallic (also small) (small reddish black texture)
04 00 00 00  |  -> roughness map (brownish/pale noise)

---

## **Table 2: ( 4 bytes ):**

Offset table

Let:
A = add [table 1 size] to every entry (above table total size)
B = Convert the 4 bytes entry to little endian
C = A + B (get relative position of every file)


-----

## **DATA:**

- GO TO OFFSET

there is a 20 bytes header

**First 8 bytes**

mipmap_byte, texture, dimension, flag0, flag1, flag2, flag3, flag4 = struct.unpack("<BBBBBBBB", data)[:8]

from here get dimensions and mipmaps 

for dimension_byte ( 1 byte )
- first 4 bits -> width
- last 4 bits  -> height

**Last 12 bytes**

either 
12, 0, 0 or
12, 0, 16777216 

where
16777216 => 1 (in big endian)
