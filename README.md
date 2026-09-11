# AI Knowledge Graph Engine

AI Knowledge Graph Engine is a Python-based tool that extracts entities and relationships from text and documents, builds a searchable knowledge graph, and provides graph-based analysis and relationship traversal.

## Features

* Entity extraction
* Relationship extraction
* Knowledge graph construction
* Entity search
* Neighbor traversal
* Multi-hop path discovery
* Relationship frequency analysis
* TXT, Markdown, CSV, and JSON support
* JSON graph export
* Interactive CLI
* Built-in demo mode

## Tech Stack

**Python | NLP | Graph Algorithms | JSON | CLI**

## DSA Used

**Dictionary | Set | defaultdict | Counter | deque | Adjacency List | BFS**

## Usage

Run interactively:

```bash
python ai_knowledge_graph_engine.py
```

Run the demo:

```bash
python ai_knowledge_graph_engine.py --demo
```

Analyze a document:

```bash
python ai_knowledge_graph_engine.py research.txt
```

Search for an entity:

```bash
python ai_knowledge_graph_engine.py research.txt --search FastAPI
```

View relationships:

```bash
python ai_knowledge_graph_engine.py research.txt --neighbors FastAPI
```

Find a path between entities:

```bash
python ai_knowledge_graph_engine.py research.txt --path FastAPI PostgreSQL
```

Export the graph:

```bash
python ai_knowledge_graph_engine.py research.txt --export knowledge_graph.json
```

## Architecture

```text
Documents
    ↓
Text Processing
    ↓
Entity Extraction
    ↓
Relationship Extraction
    ↓
Graph Construction
    ↓
Adjacency List
    ↓
Search / BFS Traversal
    ↓
JSON Export
```

## Purpose

Designed to demonstrate practical NLP, graph data structures, relationship modeling, search, and multi-hop graph traversal using Python.


