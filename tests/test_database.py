#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SnippetMind Database Tests
"""

import os
import tempfile
import unittest
from snippetmind.database import SnippetDatabase


class TestSnippetDatabase(unittest.TestCase):
    """Test cases for SnippetDatabase."""
    
    def setUp(self):
        """Set up test database."""
        self.db_fd, self.db_path = tempfile.mkstemp(suffix='.db')
        self.db = SnippetDatabase(self.db_path)
    
    def tearDown(self):
        """Clean up test database."""
        os.close(self.db_fd)
        os.unlink(self.db_path)
    
    def test_add_snippet(self):
        """Test adding a snippet."""
        success, msg = self.db.add_snippet(
            title="Test Snippet",
            code="print('hello world')",
            language="python",
            description="A test snippet",
            tags=["test", "python"]
        )
        self.assertTrue(success)
        self.assertIn("added successfully", msg)
    
    def test_duplicate_snippet(self):
        """Test duplicate detection."""
        code = "print('hello world')"
        self.db.add_snippet(title="First", code=code)
        success, msg = self.db.add_snippet(title="Second", code=code)
        self.assertFalse(success)
        self.assertIn("already exists", msg)
    
    def test_get_snippet(self):
        """Test retrieving a snippet."""
        self.db.add_snippet(title="Test", code="code here")
        snippet = self.db.get_snippet(1)
        self.assertIsNotNone(snippet)
        self.assertEqual(snippet['title'], "Test")
    
    def test_list_snippets(self):
        """Test listing snippets."""
        self.db.add_snippet(title="One", code="code1", language="python")
        self.db.add_snippet(title="Two", code="code2", language="javascript")
        
        all_snippets = self.db.list_snippets()
        self.assertEqual(len(all_snippets), 2)
        
        python_snippets = self.db.list_snippets(language="python")
        self.assertEqual(len(python_snippets), 1)
    
    def test_search_snippets(self):
        """Test searching snippets."""
        self.db.add_snippet(title="Hello World", code="print('hello')")
        self.db.add_snippet(title="Goodbye", code="print('bye')")
        
        results = self.db.search_snippets("hello")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], "Hello World")
    
    def test_update_snippet(self):
        """Test updating a snippet."""
        self.db.add_snippet(title="Old", code="old code")
        success, msg = self.db.update_snippet(1, title="New")
        self.assertTrue(success)
        
        snippet = self.db.get_snippet(1)
        self.assertEqual(snippet['title'], "New")
    
    def test_delete_snippet(self):
        """Test deleting a snippet."""
        self.db.add_snippet(title="To Delete", code="delete me")
        success, msg = self.db.delete_snippet(1)
        self.assertTrue(success)
        
        snippet = self.db.get_snippet(1)
        self.assertIsNone(snippet)
    
    def test_favorite_toggle(self):
        """Test favorite toggle."""
        self.db.add_snippet(title="Fav", code="code")
        success, status = self.db.toggle_favorite(1)
        self.assertTrue(success)
        self.assertTrue(status)
        
        success, status = self.db.toggle_favorite(1)
        self.assertFalse(status)
    
    def test_stats(self):
        """Test statistics."""
        self.db.add_snippet(title="One", code="code1", language="python")
        self.db.add_snippet(title="Two", code="code2", language="python")
        self.db.add_snippet(title="Three", code="code3", language="javascript")
        
        stats = self.db.get_stats()
        self.assertEqual(stats['total_snippets'], 3)
        self.assertEqual(len(stats['languages']), 2)
    
    def test_export_import(self):
        """Test export and import."""
        self.db.add_snippet(title="Export Test", code="export me")
        
        exported = self.db.export_snippets('json')
        self.assertIn("Export Test", exported)
        
        # Create new db and import
        db_fd2, db_path2 = tempfile.mkstemp(suffix='.db')
        db2 = SnippetDatabase(db_path2)
        
        success, failed = db2.import_snippets(exported)
        self.assertEqual(success, 1)
        
        os.close(db_fd2)
        os.unlink(db_path2)


if __name__ == '__main__':
    unittest.main()
