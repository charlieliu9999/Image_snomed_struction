from models import SnomedEntity
from typing import List, Dict, Any

def build_snomed_tree(entities: List[SnomedEntity]) -> List[SnomedEntity]:
    """
    Organizes a flat list of SnomedEntity objects into a tree structure
    based on a 'parent_code' in the relationships dictionary.
    """
    entity_map: Dict[str, SnomedEntity] = {entity.code: entity for entity in entities}
    
    # Initialize children list for all entities first
    for entity in entities:
        entity.children = []

    root_nodes: List[SnomedEntity] = []

    for entity in entities:
        parent_code = entity.relationships.get('parent_code')
        
        if parent_code and parent_code in entity_map:
            # Check to prevent adding an entity as its own child if codes are somehow identical
            if entity.code != parent_code: 
                parent_entity = entity_map[parent_code]
                parent_entity.children.append(entity)
            else:
                # If an entity's parent_code is its own code, treat it as a root to avoid recursion errors
                root_nodes.append(entity)
        else:
            # If entity has no parent_code or parent_code not in map, it's a root node
            root_nodes.append(entity)
            
    return root_nodes
