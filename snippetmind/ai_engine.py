#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SnippetMind AI Engine Module
Provides intelligent features: auto-tagging, language detection, description generation.
All processing is local - no data sent to external APIs unless explicitly configured.
"""

import re
from typing import List, Optional, Dict


class LanguageDetector:
    """Detect programming language from code content."""
    
    LANGUAGE_PATTERNS = {
        'python': [
            r'^\s*(def|class|import|from)\s+',
            r'^\s*(@\w+\s*)*(def|class)\s+',
            r'print\s*\(',
            r'\bif\s+.+\s*:\s*$',
            r'\btry\s*:\s*$',
            r'\bexcept\s+',
            r'\bfinally\s*:\s*$',
            r'\bwith\s+.+\s+as\s+',
            r'\blambda\s+',
            r'\bNone\b|\bTrue\b|\bFalse\b',
            r'\.py\b',
        ],
        'javascript': [
            r'\b(const|let|var)\s+\w+\s*=',
            r'\bfunction\s+\w+\s*\(',
            r'=>\s*\{',
            r'\bconsole\.(log|error|warn)',
            r'\bdocument\.(getElementById|querySelector)',
            r'\bwindow\.(addEventListener|onload)',
            r'require\s*\(',
            r'module\.exports',
            r'\.js\b',
        ],
        'typescript': [
            r':\s*(string|number|boolean|any|void|never)\b',
            r'\binterface\s+\w+',
            r'\btype\s+\w+\s*=',
            r'\benum\s+\w+',
            r'\bimplements\s+',
            r'\.ts\b',
        ],
        'go': [
            r'^\s*package\s+\w+',
            r'^\s*func\s+\w+',
            r'\bgo\s+func\s*\(',
            r'\bchan\s+',
            r'\bdefer\s+',
            r'\bgoroutine\b',
            r'\.go\b',
        ],
        'rust': [
            r'\bfn\s+\w+',
            r'\blet\s+mut\s+',
            r'\bimpl\s+',
            r'\bstruct\s+\w+',
            r'\benum\s+\w+',
            r'\bmatch\s+',
            r'\bOption<|Result<',
            r'\.rs\b',
        ],
        'java': [
            r'\bpublic\s+(class|interface|enum)\s+',
            r'\bprivate\s+\w+\s+\w+',
            r'\bprotected\s+',
            r'\bstatic\s+\w+',
            r'System\.(out|err)\.print',
            r'\.java\b',
        ],
        'cpp': [
            r'#include\s*<',
            r'\bstd::',
            r'\b(cout|cin|endl)\b',
            r'\b(int|float|double|char|bool)\s+\w+',
            r'\bclass\s+\w+\s*\{',
            r'\bnamespace\s+\w+',
            r'\.cpp\b|\.cc\b|\.h\b|\.hpp\b',
        ],
        'c': [
            r'#include\s*<\w+\.h>',
            r'\bprintf\s*\(',
            r'\bscanf\s*\(',
            r'\b(malloc|calloc|free)\s*\(',
            r'\b(int|float|double|char|void)\s+\w+\s*\(',
            r'\.c\b',
        ],
        'bash': [
            r'^\s*#!/bin/bash',
            r'^\s*#!/bin/sh',
            r'\becho\s+',
            r'\bif\s+\[\s+',
            r'\bfor\s+\w+\s+in\s+',
            r'\bwhile\s+\[\s+',
            r'\bdone\b',
            r'\bfi\b',
            r'\$\w+',
            r'\.sh\b',
        ],
        'sql': [
            r'\bSELECT\s+.+\s+FROM\s+',
            r'\bINSERT\s+INTO\s+',
            r'\bUPDATE\s+\w+\s+SET\s+',
            r'\bDELETE\s+FROM\s+',
            r'\bCREATE\s+(TABLE|INDEX|DATABASE)\s+',
            r'\bJOIN\s+\w+\s+ON\s+',
            r'\bWHERE\s+',
            r'\bGROUP\s+BY\s+',
            r'\bORDER\s+BY\s+',
            r'\.sql\b',
        ],
        'html': [
            r'<\w+[^>]*>',
            r'</\w+>',
            r'<!DOCTYPE\s+html',
            r'<html',
            r'\.html\b|\.htm\b',
        ],
        'css': [
            r'[.#]\w+\s*\{',
            r'@media\s+',
            r'@keyframes\s+',
            r'\b(display|position|color|background|margin|padding|border)\s*:',
            r'\.css\b',
        ],
        'json': [
            r'^\s*\{',
            r'"\w+"\s*:\s*"',
            r'"\w+"\s*:\s*(true|false|null|\d+)',
            r'\.json\b',
        ],
        'yaml': [
            r'^\w+:\s*\w+',
            r'^-\s+\w+',
            r'\.ya?ml\b',
        ],
        'dockerfile': [
            r'^\s*FROM\s+',
            r'^\s*RUN\s+',
            r'^\s*COPY\s+',
            r'^\s*ADD\s+',
            r'^\s*WORKDIR\s+',
            r'^\s*EXPOSE\s+',
            r'^\s*CMD\s+',
            r'^\s*ENTRYPOINT\s+',
            r'Dockerfile',
        ],
        'markdown': [
            r'^#{1,6}\s+',
            r'^\*\s+|^\+\s+|^-\s+',
            r'^\d+\.\s+',
            r'\[.+\]\(.+\)',
            r'```\w*',
            r'\*\*.+\*\*',
            r'\.md\b',
        ],
        'regex': [
            r'^[\^\$\.\*\+\?\[\]\(\)\{\}\|\\]',
            r'\.\*\?',
            r'\\d\+|\\w\+|\\s\+',
        ],
    }
    
    @classmethod
    def detect(cls, code: str, filename: Optional[str] = None) -> str:
        """Detect programming language from code."""
        scores = {}
        
        for lang, patterns in cls.LANGUAGE_PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, code, re.MULTILINE | re.IGNORECASE))
                score += matches
            
            # Boost score for longer matches
            if score > 0:
                scores[lang] = score
        
        # Check filename extension
        if filename:
            ext_map = {
                '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                '.go': 'go', '.rs': 'rust', '.java': 'java',
                '.cpp': 'cpp', '.cc': 'cpp', '.c': 'c', '.h': 'c',
                '.sh': 'bash', '.sql': 'sql', '.html': 'html', '.htm': 'html',
                '.css': 'css', '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
                '.md': 'markdown', '.dockerfile': 'dockerfile',
            }
            for ext, lang in ext_map.items():
                if filename.lower().endswith(ext):
                    scores[lang] = scores.get(lang, 0) + 5
        
        if scores:
            return max(scores, key=scores.get)
        return 'text'


class AutoTagger:
    """Automatically generate tags from code content."""
    
    TAG_PATTERNS = {
        'algorithm': ['sort', 'search', 'tree', 'graph', 'heap', 'queue', 'stack', 'recursive'],
        'api': ['request', 'response', 'http', 'endpoint', 'rest', 'json', 'api'],
        'async': ['async', 'await', 'promise', 'callback', 'future', 'coroutine', 'concurrent'],
        'database': ['sql', 'query', 'database', 'db', 'table', 'select', 'insert', 'update'],
        'file-io': ['file', 'read', 'write', 'open', 'close', 'path', 'directory', 'folder'],
        'network': ['socket', 'tcp', 'udp', 'http', 'url', 'request', 'client', 'server'],
        'math': ['math', 'calculate', 'sum', 'average', 'max', 'min', 'random', 'statistics'],
        'string': ['string', 'text', 'parse', 'format', 'replace', 'split', 'join', 'regex'],
        'testing': ['test', 'assert', 'mock', 'unittest', 'pytest', 'jest', 'spec'],
        'web': ['html', 'css', 'dom', 'browser', 'frontend', 'render', 'component'],
        'cli': ['command', 'argparse', 'click', 'terminal', 'console', 'argv'],
        'data': ['json', 'csv', 'xml', 'parse', 'serialize', 'data', 'dataframe'],
        'security': ['auth', 'password', 'encrypt', 'hash', 'token', 'jwt', 'oauth'],
        'error-handling': ['try', 'catch', 'except', 'error', 'exception', 'raise', 'finally'],
        'oop': ['class', 'object', 'inheritance', 'polymorphism', 'encapsulation', 'method'],
        'functional': ['lambda', 'map', 'filter', 'reduce', 'compose', 'curry', 'higher-order'],
    }
    
    @classmethod
    def generate_tags(cls, code: str, title: str = '', description: str = '') -> List[str]:
        """Generate relevant tags from code content."""
        text = f"{title} {description} {code}".lower()
        tags = []
        
        for tag, keywords in cls.TAG_PATTERNS.items():
            for keyword in keywords:
                if keyword in text:
                    tags.append(tag)
                    break
        
        # Detect language as tag
        lang = LanguageDetector.detect(code)
        if lang != 'text':
            tags.append(lang)
        
        return list(set(tags))
    
    @classmethod
    def suggest_description(cls, code: str, title: str = '') -> str:
        """Generate a simple description from code."""
        lines = code.strip().split('\n')
        
        # Look for docstrings/comments
        for line in lines[:5]:
            line = line.strip()
            if line.startswith('#') or line.startswith('//') or line.startswith('/*'):
                desc = line.lstrip('#/\* ').strip()
                if len(desc) > 10:
                    return desc
        
        # Generate from function/class names
        func_match = re.search(r'(?:def|function|fn|func)\s+(\w+)', code)
        class_match = re.search(r'(?:class|struct|interface)\s+(\w+)', code)
        
        if func_match:
            return f"Function '{func_match.group(1)}' implementation"
        elif class_match:
            return f"Class '{class_match.group(1)}' definition"
        
        # Fallback
        words = title.split() if title else ['Code']
        return f"Snippet for {' '.join(words[:3])}"


class SnippetRecommender:
    """Recommend related snippets based on content similarity."""
    
    @staticmethod
    def get_related_snippets(snippet_id: int, all_snippets: List[Dict], top_k: int = 5) -> List[Dict]:
        """Find related snippets based on language and tags."""
        target = None
        for s in all_snippets:
            if s.get('id') == snippet_id:
                target = s
                break
        
        if not target:
            return []
        
        target_lang = target.get('language', '')
        target_tags = set(target.get('tags', '').split(',')) if target.get('tags') else set()
        
        scored = []
        for s in all_snippets:
            if s.get('id') == snippet_id:
                continue
            
            score = 0
            
            # Language match
            if s.get('language') == target_lang:
                score += 3
            
            # Tag overlap
            s_tags = set(s.get('tags', '').split(',')) if s.get('tags') else set()
            tag_overlap = len(target_tags & s_tags)
            score += tag_overlap * 2
            
            if score > 0:
                s['_relevance'] = score
                scored.append(s)
        
        scored.sort(key=lambda x: x['_relevance'], reverse=True)
        return scored[:top_k]


# Convenience function
def analyze_snippet(code: str, title: str = '', filename: Optional[str] = None) -> Dict:
    """Analyze a snippet and return language, tags, and description."""
    language = LanguageDetector.detect(code, filename)
    tags = AutoTagger.generate_tags(code, title)
    description = AutoTagger.suggest_description(code, title)
    
    return {
        'language': language,
        'tags': tags,
        'description': description
    }
