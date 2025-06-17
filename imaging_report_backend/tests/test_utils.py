import unittest
import sys
import os

# Adjust path to import from the parent directory's 'services' and 'models'
# This assumes 'tests' is a subdirectory of 'imaging_report_backend'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir) # This should be 'imaging_report_backend'
sys.path.insert(0, project_root)

from services.utils import build_snomed_tree
from models import SnomedEntity

class TestBuildSnomedTree(unittest.TestCase):

    def test_simple_tree(self):
        # Test a simple parent-child relationship
        entities = [
            SnomedEntity(term="Root", code="R1", translated_term="Root_zh", relationships={}, children=[]),
            SnomedEntity(term="Child 1", code="C1", translated_term="Child1_zh", relationships={'parent_code': 'R1'}, children=[]),
            SnomedEntity(term="Child 2", code="C2", translated_term="Child2_zh", relationships={'parent_code': 'R1'}, children=[])
        ]
        tree = build_snomed_tree(entities)
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0].code, "R1")
        self.assertEqual(len(tree[0].children), 2)
        child_codes = {child.code for child in tree[0].children}
        self.assertEqual(child_codes, {"C1", "C2"})

    def test_no_parent(self):
        # Test entities with no parent, should all be roots
        entities = [
            SnomedEntity(term="Root A", code="RA", translated_term="RootA_zh", relationships={}, children=[]),
            SnomedEntity(term="Root B", code="RB", translated_term="RootB_zh", relationships={}, children=[])
        ]
        tree = build_snomed_tree(entities)
        self.assertEqual(len(tree), 2)
        root_codes = {root.code for root in tree}
        self.assertEqual(root_codes, {"RA", "RB"})

    def test_grandchild_tree(self):
        # Test a multi-level tree
        entities = [
            SnomedEntity(term="Grandparent", code="GP1", translated_term="GP1_zh", relationships={}, children=[]),
            SnomedEntity(term="Parent 1", code="P1", translated_term="P1_zh", relationships={'parent_code': 'GP1'}, children=[]),
            SnomedEntity(term="Child 1.1", code="C11", translated_term="C11_zh", relationships={'parent_code': 'P1'}, children=[])
        ]
        tree = build_snomed_tree(entities)
        self.assertEqual(len(tree), 1)
        self.assertEqual(tree[0].code, "GP1")
        self.assertEqual(len(tree[0].children), 1)
        self.assertEqual(tree[0].children[0].code, "P1")
        self.assertEqual(len(tree[0].children[0].children), 1)
        self.assertEqual(tree[0].children[0].children[0].code, "C11")

    def test_empty_list(self):
        tree = build_snomed_tree([])
        self.assertEqual(len(tree), 0)

    def test_missing_parent_in_list(self):
        # Child points to a parent not in the list
        entities = [
            SnomedEntity(term="Child Orphan", code="CO1", translated_term="CO1_zh", relationships={'parent_code': 'MISSING_PARENT'}, children=[])
        ]
        tree = build_snomed_tree(entities)
        self.assertEqual(len(tree), 1) # Orphan becomes a root
        self.assertEqual(tree[0].code, "CO1")

if __name__ == '__main__':
    # This is to allow running the tests directly from the file
    # but for the task, run_in_bash_session will be used.
    # For direct execution, ensure PYTHONPATH is set up or this script is run from imaging_report_backend directory.
    # Example: python -m tests.test_utils
    unittest.main()
