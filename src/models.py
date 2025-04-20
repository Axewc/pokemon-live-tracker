import ctypes

class Pokemon(ctypes.Structure):
    _fields_ = [
        ('species_id', ctypes.c_uint16),
        ('level', ctypes.c_uint8),
        ('_pad', ctypes.c_uint8),
        ('nickname', ctypes.c_char * 10),
        ('_unk', ctypes.c_byte * 44),  # Placeholder for unused bytes
        ('image_index', ctypes.c_uint16),
    ]