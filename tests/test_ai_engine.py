#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SnippetMind AI Engine Tests
"""

import unittest
from snippetmind.ai_engine import LanguageDetector, AutoTagger, analyze_snippet


class TestLanguageDetector(unittest.TestCase):
    """Test cases for LanguageDetector."""
    
    def test_python_detection(self):
        """Test Python code detection."""
        code = """
def hello_world():
    print("Hello, World!")
    return True

class MyClass:
    def __init__(self):
        self.value = None
"""
        lang = LanguageDetector.detect(code)
        self.assertEqual(lang, 'python')
    
    def test_javascript_detection(self):
        """Test JavaScript code detection."""
        code = """
const greeting = () => {
    console.log("Hello");
    return true;
};

function main() {
    document.querySelector('#app');
}
"""
        lang = LanguageDetector.detect(code)
        self.assertEqual(lang, 'javascript')
    
    def test_go_detection(self):
        """Test Go code detection."""
        code = """
package main

import "fmt"

func main() {
    fmt.Println("Hello")
}
"""
        lang = LanguageDetector.detect(code)
        self.assertEqual(lang, 'go')
    
    def test_sql_detection(self):
        """Test SQL detection."""
        code = """
SELECT id, name, email 
FROM users 
WHERE active = 1 
ORDER BY created_at DESC;
"""
        lang = LanguageDetector.detect(code)
        self.assertEqual(lang, 'sql')
    
    def test_filename_hint(self):
        """Test filename extension hint."""
        code = "some generic code"
        lang = LanguageDetector.detect(code, filename="script.py")
        self.assertEqual(lang, 'python')
    
    def test_unknown_code(self):
        """Test unknown code defaults to text."""
        code = "some random text without code patterns"
        lang = LanguageDetector.detect(code)
        self.assertEqual(lang, 'text')


class TestAutoTagger(unittest.TestCase):
    """Test cases for AutoTagger."""
    
    def test_tag_generation(self):
        """Test automatic tag generation."""
        code = """
def fetch_data():
    import requests
    response = requests.get('https://api.example.com')
    return response.json()
"""
        tags = AutoTagger.generate_tags(code, "API Fetcher")
        self.assertIn('api', tags)
        self.assertIn('python', tags)
    
    def test_description_generation(self):
        """Test description generation."""
        code = """
def calculate_average(numbers):
    return sum(numbers) / len(numbers)
"""
        desc = AutoTagger.suggest_description(code, "Average Calculator")
        self.assertIn("Function", desc)
    
    def test_database_tags(self):
        """Test database-related tags."""
        code = """
SELECT * FROM users WHERE id = 1;
INSERT INTO logs (message) VALUES ('test');
"""
        tags = AutoTagger.generate_tags(code)
        self.assertIn('database', tags)
        self.assertIn('sql', tags)


class TestAnalyzeSnippet(unittest.TestCase):
    """Test the analyze_snippet convenience function."""
    
    def test_full_analysis(self):
        """Test complete snippet analysis."""
        code = """
# Calculate factorial
 def factorial(n):
     if n <= 1:
         return 1
     return n * factorial(n - 1)
 """
        result = analyze_snippet(code, "Factorial Function")
        
        self.assertEqual(result['language'], 'python')
        self.assertIn('python', result['tags'])
        self.assertIsNotNone(result['description'])


if __name__ == '__main__':
    unittest.main()
