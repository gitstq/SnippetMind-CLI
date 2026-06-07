#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SnippetMind Database Module
Handles all SQLite operations for snippet storage, search, and management.
"""

import sqlite3
import json
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from contextlib import contextmanager


class SnippetDatabase:
    """SQLite database manager for code snippets."""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize database connection."""
        if db_path is None:
            config_dir = os.path.expanduser('~/.snippetmind')
            os.makedirs(config_dir, exist_ok=True)
            db_path = os.path.join(config_dir, 'snippets.db')
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize database schema."""
        with self._get_connection() as conn:
            # Main snippets table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS snippets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    code TEXT NOT NULL,
                    language TEXT,
                    description TEXT,
                    tags TEXT,
                    source TEXT,
                    hash TEXT UNIQUE NOT NULL,
                    usage_count INTEGER DEFAULT 0,
                    favorite INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Full-text search virtual table
            conn.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS snippets_fts USING fts5(
                    title, code, description, language,
                    content='snippets',
                    content_rowid='id'
                )
            ''')
            
            # Triggers to keep FTS index in sync
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS snippets_ai AFTER INSERT ON snippets BEGIN
                    INSERT INTO snippets_fts(rowid, title, code, description, language)
                    VALUES (new.id, new.title, new.code, new.description, new.language);
                END
            ''')
            
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS snippets_ad AFTER DELETE ON snippets BEGIN
                    INSERT INTO snippets_fts(snippets_fts, rowid, title, code, description, language)
                    VALUES ('delete', old.id, old.title, old.code, old.description, old.language);
                END
            ''')
            
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS snippets_au AFTER UPDATE ON snippets BEGIN
                    INSERT INTO snippets_fts(snippets_fts, rowid, title, code, description, language)
                    VALUES ('delete', old.id, old.title, old.code, old.description, old.language);
                    INSERT INTO snippets_fts(rowid, title, code, description, language)
                    VALUES (new.id, new.title, new.code, new.description, new.language);
                END
            ''')
            
            # Collections table for organizing snippets
            conn.execute('''
                CREATE TABLE IF NOT EXISTS collections (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Snippet-Collection junction table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS snippet_collections (
                    snippet_id INTEGER,
                    collection_id INTEGER,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (snippet_id, collection_id),
                    FOREIGN KEY (snippet_id) REFERENCES snippets(id) ON DELETE CASCADE,
                    FOREIGN KEY (collection_id) REFERENCES collections(id) ON DELETE CASCADE
                )
            ''')
            
            # Indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_snippets_language ON snippets(language)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_snippets_favorite ON snippets(favorite)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_snippets_created ON snippets(created_at)')
    
    def _compute_hash(self, code: str) -> str:
        """Compute MD5 hash of code for deduplication."""
        return hashlib.md5(code.strip().encode('utf-8')).hexdigest()
    
    def add_snippet(self, title: str, code: str, language: Optional[str] = None,
                    description: Optional[str] = None, tags: Optional[List[str]] = None,
                    source: Optional[str] = None) -> Tuple[bool, str]:
        """Add a new snippet. Returns (success, message)."""
        code_hash = self._compute_hash(code)
        tags_str = ','.join(tags) if tags else ''
        
        with self._get_connection() as conn:
            # Check for duplicates
            existing = conn.execute(
                'SELECT id FROM snippets WHERE hash = ?', (code_hash,)
            ).fetchone()
            
            if existing:
                return False, f"Snippet already exists (ID: {existing['id']})"
            
            cursor = conn.execute('''
                INSERT INTO snippets (title, code, language, description, tags, source, hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (title, code, language or 'text', description or '', tags_str, source or '', code_hash))
            
            return True, f"Snippet added successfully (ID: {cursor.lastrowid})"
    
    def get_snippet(self, snippet_id: int) -> Optional[Dict]:
        """Get a single snippet by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                'SELECT * FROM snippets WHERE id = ?', (snippet_id,)
            ).fetchone()
            
            if row:
                return dict(row)
            return None
    
    def list_snippets(self, language: Optional[str] = None, 
                      favorite_only: bool = False,
                      tag: Optional[str] = None,
                      limit: int = 50, offset: int = 0) -> List[Dict]:
        """List snippets with optional filters."""
        with self._get_connection() as conn:
            query = 'SELECT * FROM snippets WHERE 1=1'
            params = []
            
            if language:
                query += ' AND language = ?'
                params.append(language.lower())
            
            if favorite_only:
                query += ' AND favorite = 1'
            
            if tag:
                query += ' AND (tags LIKE ? OR tags LIKE ? OR tags = ?)'
                params.append(f'%,{tag},%')
                params.append(f'{tag},%')
                params.append(tag)
            
            query += ' ORDER BY updated_at DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])
            
            rows = conn.execute(query, params).fetchall()
            return [dict(row) for row in rows]
    
    def search_snippets(self, query: str, language: Optional[str] = None) -> List[Dict]:
        """Full-text search snippets."""
        with self._get_connection() as conn:
            # Build FTS query
            fts_query = ' '.join(f'{term}*' for term in query.split())
            
            sql = '''
                SELECT s.*, rank
                FROM snippets s
                JOIN snippets_fts fts ON s.id = fts.rowid
                WHERE snippets_fts MATCH ?
            '''
            params = [fts_query]
            
            if language:
                sql += ' AND s.language = ?'
                params.append(language.lower())
            
            sql += ' ORDER BY rank LIMIT 50'
            
            rows = conn.execute(sql, params).fetchall()
            return [dict(row) for row in rows]
    
    def semantic_search(self, query: str, snippets: List[Dict], top_k: int = 10) -> List[Dict]:
        """Simple keyword-based semantic search fallback."""
        query_terms = set(query.lower().split())
        scored = []
        
        for snippet in snippets:
            score = 0
            text = f"{snippet.get('title', '')} {snippet.get('description', '')} {snippet.get('code', '')} {snippet.get('tags', '')}".lower()
            
            for term in query_terms:
                if term in text:
                    score += text.count(term)
            
            if score > 0:
                snippet['_score'] = score
                scored.append(snippet)
        
        scored.sort(key=lambda x: x['_score'], reverse=True)
        return scored[:top_k]
    
    def update_snippet(self, snippet_id: int, **kwargs) -> Tuple[bool, str]:
        """Update snippet fields."""
        allowed_fields = {'title', 'code', 'language', 'description', 'tags', 'source', 'favorite'}
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
        
        if not updates:
            return False, "No valid fields to update"
        
        if 'code' in updates:
            updates['hash'] = self._compute_hash(updates['code'])
        
        updates['updated_at'] = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            # Check if snippet exists
            existing = conn.execute(
                'SELECT id FROM snippets WHERE id = ?', (snippet_id,)
            ).fetchone()
            
            if not existing:
                return False, f"Snippet {snippet_id} not found"
            
            set_clause = ', '.join(f'{k} = ?' for k in updates.keys())
            values = list(updates.values()) + [snippet_id]
            
            conn.execute(f'UPDATE snippets SET {set_clause} WHERE id = ?', values)
            return True, f"Snippet {snippet_id} updated successfully"
    
    def delete_snippet(self, snippet_id: int) -> Tuple[bool, str]:
        """Delete a snippet."""
        with self._get_connection() as conn:
            cursor = conn.execute('DELETE FROM snippets WHERE id = ?', (snippet_id,))
            
            if cursor.rowcount > 0:
                return True, f"Snippet {snippet_id} deleted"
            return False, f"Snippet {snippet_id} not found"
    
    def increment_usage(self, snippet_id: int):
        """Increment usage counter for a snippet."""
        with self._get_connection() as conn:
            conn.execute(
                'UPDATE snippets SET usage_count = usage_count + 1, updated_at = ? WHERE id = ?',
                (datetime.now().isoformat(), snippet_id)
            )
    
    def toggle_favorite(self, snippet_id: int) -> Tuple[bool, bool]:
        """Toggle favorite status. Returns (success, new_status)."""
        with self._get_connection() as conn:
            row = conn.execute(
                'SELECT favorite FROM snippets WHERE id = ?', (snippet_id,)
            ).fetchone()
            
            if not row:
                return False, False
            
            new_status = 1 - row['favorite']
            conn.execute(
                'UPDATE snippets SET favorite = ?, updated_at = ? WHERE id = ?',
                (new_status, datetime.now().isoformat(), snippet_id)
            )
            return True, bool(new_status)
    
    def get_stats(self) -> Dict:
        """Get database statistics."""
        with self._get_connection() as conn:
            total = conn.execute('SELECT COUNT(*) as count FROM snippets').fetchone()['count']
            favorites = conn.execute('SELECT COUNT(*) as count FROM snippets WHERE favorite = 1').fetchone()['count']
            
            languages = conn.execute('''
                SELECT language, COUNT(*) as count 
                FROM snippets 
                GROUP BY language 
                ORDER BY count DESC
            ''').fetchall()
            
            most_used = conn.execute('''
                SELECT id, title, usage_count 
                FROM snippets 
                ORDER BY usage_count DESC 
                LIMIT 5
            ''').fetchall()
            
            return {
                'total_snippets': total,
                'favorites': favorites,
                'languages': [dict(row) for row in languages],
                'most_used': [dict(row) for row in most_used]
            }
    
    def get_languages(self) -> List[str]:
        """Get all unique languages."""
        with self._get_connection() as conn:
            rows = conn.execute(
                'SELECT DISTINCT language FROM snippets ORDER BY language'
            ).fetchall()
            return [row['language'] for row in rows if row['language']]
    
    def get_tags(self) -> List[str]:
        """Get all unique tags."""
        with self._get_connection() as conn:
            rows = conn.execute('SELECT tags FROM snippets WHERE tags != ""').fetchall()
            tags = set()
            for row in rows:
                for tag in row['tags'].split(','):
                    tag = tag.strip()
                    if tag:
                        tags.add(tag)
            return sorted(list(tags))
    
    def export_snippets(self, format_type: str = 'json') -> str:
        """Export all snippets to JSON or Markdown."""
        snippets = self.list_snippets(limit=10000)
        
        if format_type == 'json':
            return json.dumps(snippets, indent=2, ensure_ascii=False, default=str)
        
        elif format_type == 'markdown':
            md = "# SnippetMind Export\n\n"
            for s in snippets:
                md += f"## {s['title']}\n\n"
                md += f"**Language:** {s['language']}  \n"
                md += f"**Tags:** {s['tags']}  \n"
                md += f"**Description:** {s['description']}\n\n"
                md += f"```{s['language']}\n{s['code']}\n```\n\n"
                md += "---\n\n"
            return md
        
        return ""
    
    def import_snippets(self, data: str, format_type: str = 'json') -> Tuple[int, int]:
        """Import snippets from JSON. Returns (success_count, fail_count)."""
        success = 0
        failed = 0
        
        try:
            snippets = json.loads(data)
            if isinstance(snippets, dict):
                snippets = [snippets]
            
            for snippet in snippets:
                try:
                    ok, _ = self.add_snippet(
                        title=snippet.get('title', 'Untitled'),
                        code=snippet.get('code', ''),
                        language=snippet.get('language'),
                        description=snippet.get('description'),
                        tags=snippet.get('tags', []),
                        source=snippet.get('source')
                    )
                    if ok:
                        success += 1
                    else:
                        failed += 1
                except Exception:
                    failed += 1
        except json.JSONDecodeError:
            failed += 1
        
        return success, failed
    
    def create_collection(self, name: str, description: str = '') -> Tuple[bool, str]:
        """Create a new collection."""
        with self._get_connection() as conn:
            try:
                cursor = conn.execute(
                    'INSERT INTO collections (name, description) VALUES (?, ?)',
                    (name, description)
                )
                return True, f"Collection '{name}' created (ID: {cursor.lastrowid})"
            except sqlite3.IntegrityError:
                return False, f"Collection '{name}' already exists"
    
    def add_to_collection(self, snippet_id: int, collection_id: int) -> Tuple[bool, str]:
        """Add snippet to collection."""
        with self._get_connection() as conn:
            try:
                conn.execute(
                    'INSERT INTO snippet_collections (snippet_id, collection_id) VALUES (?, ?)',
                    (snippet_id, collection_id)
                )
                return True, f"Snippet {snippet_id} added to collection {collection_id}"
            except sqlite3.IntegrityError:
                return False, "Snippet already in collection"
    
    def get_collections(self) -> List[Dict]:
        """Get all collections."""
        with self._get_connection() as conn:
            rows = conn.execute('SELECT * FROM collections ORDER BY name').fetchall()
            return [dict(row) for row in rows]
