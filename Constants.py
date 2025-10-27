"""
POD Constants
Author: Johnny Shumway (jShum00), adapted from Dummiesman.

This is a data class used by PyPOD, it is based on the data found in Dummiesman's
Constants.cs for his Poddy program, this is used for find header and entry data for
the extractor.

https://github.com/Dummiesman/Poddy/tree/main/PODTool
"""

@dataclass
class Constants:
    # ---- EPD1 ----
    EPD1_HEADER_SIZE = 0x110
    EPD1_ENTRY_SIZE  = 0x50

    # ---- POD1 ----
    POD1_HEADER_SIZE = 0x54
    POD1_ENTRY_SIZE  = 0x28

    # ---- POD2 ----
    POD2_HEADER_SIZE = 0x60   # 96 bytes
    POD2_ENTRY_SIZE  = 0x14   # 20 bytes

    # ---- POD3 ----
    POD3_HEADER_SIZE = 0x120  # 288 bytes
    POD3_ENTRY_SIZE  = 0x14   # 20 bytes

