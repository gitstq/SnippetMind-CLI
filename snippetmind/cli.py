#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SnippetMind-CLI: Main Command Line Interface
Provides all user-facing commands for snippet management.
"""

import os
import sys
import json
import pyperclip
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
from rich import box

from .database import SnippetDatabase
from .ai_engine import analyze_snippet, SnippetRecommender

console = Console()

# Custom context to pass database instance
pass_db = click.make_pass_decorator(SnippetDatabase, ensure=True)


def get_db():
    """Get or create database instance."""
    return SnippetDatabase()


@click.group()
@click.version_option(version='1.0.0', prog_name='snippetmind')
@click.pass_context
def cli(ctx):
    """🧠 SnippetMind-CLI: AI-Powered Smart Code Snippet Manager
    
    Manage your code snippets with semantic search, auto-tagging, and intelligent recommendations.
    
    Quick Start:
        sm add           Add a new snippet
        sm search        Search snippets
        sm list          List all snippets
        sm show          Show snippet details
    """
    ctx.ensure_object(dict)
    ctx.obj['db'] = get_db()


@cli.command()
@click.option('--title', '-t', prompt='Title', help='Snippet title')
@click.option('--code', '-c', prompt='Code (Ctrl+D or EOF to finish)', help='Code content')
@click.option('--language', '-l', help='Programming language (auto-detected if not specified)')
@click.option('--description', '-d', help='Snippet description')
@click.option('--tags', help='Comma-separated tags')
@click.option('--source', '-s', help='Source URL or reference')
@click.option('--from-clipboard', '-p', is_flag=True, help='Read code from clipboard')
@click.option('--from-file', '-f', type=click.Path(exists=True), help='Read code from file')
@click.pass_context
def add(ctx, title, code, language, description, tags, source, from_clipboard, from_file):
    """➕ Add a new code snippet"""
    db = ctx.obj['db']
    
    # Handle input sources
    if from_clipboard:
        try:
            code = pyperclip.paste()
            console.print("[green]✓ Code loaded from clipboard[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to read clipboard: {e}[/red]")
            return
    
    elif from_file:
        try:
            with open(from_file, 'r', encoding='utf-8') as f:
                code = f.read()
            console.print(f"[green]✓ Code loaded from {from_file}[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to read file: {e}[/red]")
            return
    
    # If code is empty or default, prompt for multi-line input
    if not code or code == 'Code (Ctrl+D or EOF to finish)':
        console.print("[yellow]Enter your code below (Ctrl+D or empty line to finish):[/yellow]")
        lines = []
        try:
            while True:
                line = input()
                if line == '':
                    break
                lines.append(line)
        except EOFError:
            pass
        code = '\n'.join(lines)
    
    if not code.strip():
        console.print("[red]✗ Code cannot be empty[/red]")
        return
    
    # AI Analysis
    with console.status("[bold green]Analyzing snippet with AI..."):
        analysis = analyze_snippet(code, title, from_file)
    
    # Auto-detect language if not provided
    if not language:
        language = analysis['language']
        console.print(f"[blue]ℹ Auto-detected language: {language}[/blue]")
    
    # Auto-generate description if not provided
    if not description:
        description = analysis['description']
        console.print(f"[blue]ℹ Auto-generated description: {description}[/blue]")
    
    # Auto-generate tags if not provided
    tag_list = []
    if tags:
        tag_list = [t.strip() for t in tags.split(',')]
    else:
        tag_list = analysis['tags']
        if tag_list:
            console.print(f"[blue]ℹ Auto-generated tags: {', '.join(tag_list)}[/blue]")
    
    # Preview
    console.print("\n[bold]Preview:[/bold]")
    console.print(Panel(
        Syntax(code, language or 'text', theme='monokai', line_numbers=True),
        title=f"📄 {title}",
        subtitle=f"Language: {language} | Tags: {', '.join(tag_list)}"
    ))
    
    if Confirm.ask("Save this snippet?"):
        success, msg = db.add_snippet(
            title=title,
            code=code,
            language=language,
            description=description,
            tags=tag_list,
            source=source
        )
        
        if success:
            console.print(f"[green]✓ {msg}[/green]")
        else:
            console.print(f"[yellow]⚠ {msg}[/yellow]")
    else:
        console.print("[yellow]Cancelled[/yellow]")


@cli.command()
@click.argument('query')
@click.option('--language', '-l', help='Filter by language')
@click.option('--semantic', '-s', is_flag=True, help='Use semantic search')
@click.pass_context
def search(ctx, query, language, semantic):
    """🔍 Search snippets by keyword or semantic similarity"""
    db = ctx.obj['db']
    
    with console.status(f"[bold green]Searching for '{query}'..."):
        if semantic:
            # Get all snippets then do semantic ranking
            all_snippets = db.list_snippets(language=language, limit=1000)
            results = db.semantic_search(query, all_snippets)
        else:
            results = db.search_snippets(query, language=language)
    
    if not results:
        console.print(f"[yellow]No snippets found for '{query}'[/yellow]")
        return
    
    console.print(f"[green]✓ Found {len(results)} snippet(s)[/green]\n")
    
    table = Table(
        title=f"🔍 Search Results: '{query}'",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    table.add_column("ID", style="cyan", width=6)
    table.add_column("Title", style="green", width=30)
    table.add_column("Language", style="yellow", width=12)
    table.add_column("Tags", style="blue", width=25)
    table.add_column("Description", style="white", width=40)
    
    for snippet in results:
        table.add_row(
            str(snippet['id']),
            snippet['title'][:28],
            snippet.get('language', 'text')[:10],
            (snippet.get('tags', '') or '-')[:23],
            (snippet.get('description', '') or '-')[:38]
        )
    
    console.print(table)


@cli.command()
@click.option('--language', '-l', help='Filter by language')
@click.option('--favorite', '-f', is_flag=True, help='Show favorites only')
@click.option('--tag', '-t', help='Filter by tag')
@click.option('--limit', '-n', default=20, help='Number of snippets to show')
@click.pass_context
def list(ctx, language, favorite, tag, limit):
    """📋 List all snippets with optional filters"""
    db = ctx.obj['db']
    
    snippets = db.list_snippets(
        language=language,
        favorite_only=favorite,
        tag=tag,
        limit=limit
    )
    
    if not snippets:
        filters = []
        if language:
            filters.append(f"language={language}")
        if favorite:
            filters.append("favorites")
        if tag:
            filters.append(f"tag={tag}")
        
        filter_str = f" ({', '.join(filters)})" if filters else ""
        console.print(f"[yellow]No snippets found{filter_str}[/yellow]")
        return
    
    table = Table(
        title="📋 Your Snippets",
        box=box.ROUNDED,
        show_header=True,
        header_style="bold magenta"
    )
    table.add_column("ID", style="cyan", width=6)
    table.add_column("★", style="yellow", width=3)
    table.add_column("Title", style="green", width=28)
    table.add_column("Language", style="yellow", width=10)
    table.add_column("Tags", style="blue", width=20)
    table.add_column("Used", style="magenta", width=6)
    table.add_column("Updated", style="dim", width=16)
    
    for s in snippets:
        table.add_row(
            str(s['id']),
            "★" if s.get('favorite') else "",
            s['title'][:26],
            (s.get('language', '') or 'text')[:8],
            (s.get('tags', '') or '-')[:18],
            str(s.get('usage_count', 0)),
            s.get('updated_at', '')[:16]
        )
    
    console.print(table)
    console.print(f"\n[dim]Showing {len(snippets)} snippet(s)[/dim]")


@cli.command()
@click.argument('snippet_id', type=int)
@click.option('--copy', '-c', is_flag=True, help='Copy code to clipboard')
@click.option('--related', '-r', is_flag=True, help='Show related snippets')
@click.pass_context
def show(ctx, snippet_id, copy, related):
    """📄 Show snippet details with syntax highlighting"""
    db = ctx.obj['db']
    
    snippet = db.get_snippet(snippet_id)
    if not snippet:
        console.print(f"[red]✗ Snippet {snippet_id} not found[/red]")
        return
    
    # Increment usage
    db.increment_usage(snippet_id)
    
    # Display snippet
    language = snippet.get('language', 'text')
    code = snippet.get('code', '')
    
    console.print(Panel(
        Syntax(code, language, theme='monokai', line_numbers=True),
        title=f"📄 {snippet['title']} [ID: {snippet_id}]",
        subtitle=f"Language: {language} | ★: {'Yes' if snippet.get('favorite') else 'No'} | Used: {snippet.get('usage_count', 0)} times"
    ))
    
    # Metadata
    info_table = Table(show_header=False, box=box.SIMPLE)
    info_table.add_column("Field", style="bold cyan")
    info_table.add_column("Value", style="white")
    
    info_table.add_row("Description", snippet.get('description', '-') or '-')
    info_table.add_row("Tags", snippet.get('tags', '-') or '-')
    info_table.add_row("Source", snippet.get('source', '-') or '-')
    info_table.add_row("Created", snippet.get('created_at', '-') or '-')
    info_table.add_row("Updated", snippet.get('updated_at', '-') or '-')
    
    console.print(info_table)
    
    if copy:
        try:
            pyperclip.copy(code)
            console.print("[green]✓ Code copied to clipboard[/green]")
        except Exception as e:
            console.print(f"[red]✗ Failed to copy: {e}[/red]")
    
    if related:
        all_snippets = db.list_snippets(limit=1000)
        related_snippets = SnippetRecommender.get_related_snippets(snippet_id, all_snippets)
        
        if related_snippets:
            console.print("\n[bold]Related Snippets:[/bold]")
            for rs in related_snippets:
                console.print(f"  [cyan]{rs['id']}[/cyan] [green]{rs['title']}[/green] [dim](relevance: {rs['_relevance']})[/dim]")


@cli.command()
@click.argument('snippet_id', type=int)
@click.pass_context
def copy(ctx, snippet_id):
    """📋 Copy snippet code to clipboard"""
    db = ctx.obj['db']
    
    snippet = db.get_snippet(snippet_id)
    if not snippet:
        console.print(f"[red]✗ Snippet {snippet_id} not found[/red]")
        return
    
    try:
        pyperclip.copy(snippet['code'])
        db.increment_usage(snippet_id)
        console.print(f"[green]✓ Snippet '{snippet['title']}' copied to clipboard[/green]")
    except Exception as e:
        console.print(f"[red]✗ Failed to copy: {e}[/red]")


@cli.command()
@click.argument('snippet_id', type=int)
@click.pass_context
def favorite(ctx, snippet_id):
    """⭐ Toggle favorite status for a snippet"""
    db = ctx.obj['db']
    
    success, status = db.toggle_favorite(snippet_id)
    if success:
        state = "★ favorited" if status else "☆ unfavorited"
        console.print(f"[green]✓ Snippet {snippet_id} {state}[/green]")
    else:
        console.print(f"[red]✗ Snippet {snippet_id} not found[/red]")


@cli.command()
@click.argument('snippet_id', type=int)
@click.option('--title', '-t', help='New title')
@click.option('--code', '-c', help='New code')
@click.option('--language', '-l', help='New language')
@click.option('--description', '-d', help='New description')
@click.option('--tags', help='New comma-separated tags')
@click.option('--source', '-s', help='New source')
@click.pass_context
def edit(ctx, snippet_id, title, code, language, description, tags, source):
    """✏️ Edit an existing snippet"""
    db = ctx.obj['db']
    
    updates = {}
    if title:
        updates['title'] = title
    if code:
        updates['code'] = code
    if language:
        updates['language'] = language
    if description:
        updates['description'] = description
    if tags is not None:
        updates['tags'] = tags
    if source is not None:
        updates['source'] = source
    
    if not updates:
        console.print("[yellow]No fields to update. Use --help for options.[/yellow]")
        return
    
    success, msg = db.update_snippet(snippet_id, **updates)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


@cli.command()
@click.argument('snippet_id', type=int)
@click.confirmation_option(prompt='Are you sure you want to delete this snippet?')
@click.pass_context
def delete(ctx, snippet_id):
    """🗑️ Delete a snippet"""
    db = ctx.obj['db']
    
    success, msg = db.delete_snippet(snippet_id)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[red]✗ {msg}[/red]")


@cli.command()
@click.pass_context
def stats(ctx):
    """📊 Show database statistics"""
    db = ctx.obj['db']
    
    stats_data = db.get_stats()
    
    console.print(Panel(
        f"[bold cyan]Total Snippets:[/bold cyan] {stats_data['total_snippets']}\n"
        f"[bold yellow]Favorites:[/bold yellow] {stats_data['favorites']}\n",
        title="📊 SnippetMind Statistics",
        box=box.ROUNDED
    ))
    
    if stats_data['languages']:
        console.print("\n[bold]Languages:[/bold]")
        lang_table = Table(show_header=True, header_style="bold magenta", box=box.SIMPLE)
        lang_table.add_column("Language", style="cyan")
        lang_table.add_column("Count", style="green", justify="right")
        
        for lang in stats_data['languages']:
            lang_table.add_row(lang['language'], str(lang['count']))
        console.print(lang_table)
    
    if stats_data['most_used']:
        console.print("\n[bold]Most Used:[/bold]")
        for item in stats_data['most_used']:
            console.print(f"  [cyan]{item['id']}[/cyan] [green]{item['title']}[/green] [dim](used {item['usage_count']} times)[/dim]")


@cli.command()
@click.option('--format', 'fmt', type=click.Choice(['json', 'markdown']), default='json',
              help='Export format')
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.pass_context
def export(ctx, fmt, output):
    """📤 Export snippets to JSON or Markdown"""
    db = ctx.obj['db']
    
    with console.status("[bold green]Exporting snippets..."):
        data = db.export_snippets(fmt)
    
    if output:
        with open(output, 'w', encoding='utf-8') as f:
            f.write(data)
        console.print(f"[green]✓ Exported to {output}[/green]")
    else:
        console.print(data)


@cli.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.pass_context
def import_snippets(ctx, file_path):
    """📥 Import snippets from JSON file"""
    db = ctx.obj['db']
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = f.read()
        
        with console.status("[bold green]Importing snippets..."):
            success, failed = db.import_snippets(data)
        
        console.print(f"[green]✓ Imported {success} snippet(s)[/green]")
        if failed:
            console.print(f"[yellow]⚠ {failed} snippet(s) failed (duplicates or errors)[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Import failed: {e}[/red]")


@cli.command()
@click.pass_context
def languages(ctx):
    """🌐 List all languages in your snippet collection"""
    db = ctx.obj['db']
    
    langs = db.get_languages()
    if not langs:
        console.print("[yellow]No snippets found[/yellow]")
        return
    
    console.print("[bold]Languages in your collection:[/bold]")
    for lang in langs:
        console.print(f"  • {lang}")


@cli.command()
@click.pass_context
def tags(ctx):
    """🏷️ List all tags in your snippet collection"""
    db = ctx.obj['db']
    
    tags_list = db.get_tags()
    if not tags_list:
        console.print("[yellow]No tags found[/yellow]")
        return
    
    console.print("[bold]Tags in your collection:[/bold]")
    tag_items = [f"[cyan]{tag}[/cyan]" for tag in tags_list]
    console.print(Columns(tag_items, equal=True))


# Collection management commands
@cli.group()
def collection():
    """📁 Manage snippet collections"""
    pass


@collection.command('create')
@click.argument('name')
@click.option('--description', '-d', default='')
@click.pass_context
def collection_create(ctx, name, description):
    """📁 Create a new collection"""
    db = ctx.obj['db']
    success, msg = db.create_collection(name, description)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[yellow]⚠ {msg}[/yellow]")


@collection.command('list')
@click.pass_context
def collection_list(ctx):
    """📋 List all collections"""
    db = ctx.obj['db']
    collections = db.get_collections()
    
    if not collections:
        console.print("[yellow]No collections found[/yellow]")
        return
    
    table = Table(title="📁 Collections", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Description", style="white")
    
    for c in collections:
        table.add_row(str(c['id']), c['name'], c.get('description', '') or '-')
    
    console.print(table)


@collection.command('add')
@click.argument('snippet_id', type=int)
@click.argument('collection_id', type=int)
@click.pass_context
def collection_add(ctx, snippet_id, collection_id):
    """➕ Add snippet to collection"""
    db = ctx.obj['db']
    success, msg = db.add_to_collection(snippet_id, collection_id)
    if success:
        console.print(f"[green]✓ {msg}[/green]")
    else:
        console.print(f"[yellow]⚠ {msg}[/yellow]")


# Interactive mode
@cli.command()
@click.pass_context
def interactive(ctx):
    """🎮 Launch interactive mode"""
    console.print(Panel(
        "[bold green]Welcome to SnippetMind Interactive Mode![/bold green]\n\n"
        "Commands:\n"
        "  add     - Add a new snippet\n"
        "  search  - Search snippets\n"
        "  list    - List all snippets\n"
        "  show    - Show snippet details\n"
        "  copy    - Copy snippet to clipboard\n"
        "  fav     - Toggle favorite\n"
        "  stats   - Show statistics\n"
        "  quit    - Exit interactive mode",
        title="🧠 SnippetMind Interactive",
        box=box.ROUNDED
    ))
    
    db = ctx.obj['db']
    
    while True:
        try:
            cmd = Prompt.ask("\n[bold cyan]snippetmind[/bold cyan]").strip().lower()
            
            if cmd == 'quit' or cmd == 'exit':
                console.print("[green]Goodbye! 👋[/green]")
                break
            
            elif cmd == 'add':
                title = Prompt.ask("Title")
                console.print("Enter code (empty line to finish):")
                lines = []
                while True:
                    line = input()
                    if line == '':
                        break
                    lines.append(line)
                code = '\n'.join(lines)
                
                if code.strip():
                    analysis = analyze_snippet(code, title)
                    success, msg = db.add_snippet(
                        title=title,
                        code=code,
                        language=analysis['language'],
                        description=analysis['description'],
                        tags=analysis['tags']
                    )
                    console.print(f"[green]✓ {msg}[/green]" if success else f"[yellow]⚠ {msg}[/yellow]")
            
            elif cmd == 'search':
                query = Prompt.ask("Search query")
                results = db.search_snippets(query)
                if results:
                    for r in results:
                        console.print(f"  [cyan]{r['id']}[/cyan] [green]{r['title']}[/green]")
                else:
                    console.print("[yellow]No results[/yellow]")
            
            elif cmd == 'list':
                snippets = db.list_snippets(limit=20)
                for s in snippets:
                    fav = "★" if s.get('favorite') else " "
                    console.print(f"  [cyan]{s['id']}[/cyan]{fav} [green]{s['title']}[/green] [{s.get('language', 'text')}]")
            
            elif cmd == 'show':
                sid = int(Prompt.ask("Snippet ID"))
                snippet = db.get_snippet(sid)
                if snippet:
                    console.print(Syntax(snippet['code'], snippet.get('language', 'text'), theme='monokai'))
                else:
                    console.print("[red]Not found[/red]")
            
            elif cmd == 'copy':
                sid = int(Prompt.ask("Snippet ID"))
                snippet = db.get_snippet(sid)
                if snippet:
                    pyperclip.copy(snippet['code'])
                    db.increment_usage(sid)
                    console.print("[green]✓ Copied![/green]")
                else:
                    console.print("[red]Not found[/red]")
            
            elif cmd == 'fav':
                sid = int(Prompt.ask("Snippet ID"))
                success, status = db.toggle_favorite(sid)
                if success:
                    state = "★" if status else "☆"
                    console.print(f"[green]✓ {state}[/green]")
            
            elif cmd == 'stats':
                stats_data = db.get_stats()
                console.print(f"Total: {stats_data['total_snippets']} | Favorites: {stats_data['favorites']}")
            
            else:
                console.print("[yellow]Unknown command. Type 'help' for available commands.[/yellow]")
        
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'quit' to exit[/yellow]")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def main():
    """Entry point for the CLI."""
    cli()


if __name__ == '__main__':
    main()
