from src.models import Pokemon

def parse_pokemon(raw_data: bytes) -> Pokemon:
    return Pokemon.from_buffer_copy(raw_data)

def get_team(memory_client, base_offset, struct_size) -> list:
    team = []
    for i in range(6):
        address = base_offset + i * struct_size
        raw_data = memory_client.read_memory(address, struct_size)
        pokemon = parse_pokemon(raw_data)
        if pokemon.species_id == 0:
            continue  # Slot vacío
        team.append(pokemon)
    return team