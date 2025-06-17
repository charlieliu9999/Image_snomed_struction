from models import SnomedEntity # Changed to absolute import
from typing import List, Dict, Any

def build_snomed_tree(entities: List[SnomedEntity]) -> List[SnomedEntity]:
    """
    Organizes a flat list of SnomedEntity objects into a tree structure
    based on a 'parent_code' in the relationships dictionary.
    Assumes SnomedEntity objects in 'entities' list can be modified (their .children list).
    """
    entity_map: Dict[str, SnomedEntity] = {entity.code: entity for entity in entities}

    # Initialize children list for all entities first to ensure they are clean
    for entity in entities:
        entity.children = []

    root_nodes: List[SnomedEntity] = []

    for entity in entities:
        parent_code = entity.relationships.get('parent_code')

        if parent_code and parent_code in entity_map:
            # Ensure not adding an entity as its own child if codes are somehow identical
            # and also ensure the parent is not the entity itself.
            if entity.code != parent_code:
                parent_entity = entity_map[parent_code]
                parent_entity.children.append(entity)
            else:
                # If an entity's parent_code is its own code, or if it has no valid parent,
                # it's considered a root node for the purpose of this tree construction.
                root_nodes.append(entity)
        else:
            # If entity has no parent_code or parent_code not in map, it's a root node
            root_nodes.append(entity)

    return root_nodes
