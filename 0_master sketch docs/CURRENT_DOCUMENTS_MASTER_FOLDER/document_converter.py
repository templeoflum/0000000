"""
Document Converter - Converts text/docx files to AI-parseable JSON format
with metadata extraction, concept identification, and cross-referencing.
"""

import os
import json
import re
import hashlib
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Set, Tuple

# Try to import docx, install if not available
try:
    from docx import Document
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Warning: python-docx not installed. Run: pip install python-docx")

# Try to import PDF library
try:
    import fitz  # PyMuPDF
    PDF_AVAILABLE = True
    PDF_LIB = 'pymupdf'
except ImportError:
    try:
        from PyPDF2 import PdfReader
        PDF_AVAILABLE = True
        PDF_LIB = 'pypdf2'
    except ImportError:
        PDF_AVAILABLE = False
        PDF_LIB = None
        print("Warning: No PDF library installed. Run: pip install PyMuPDF (recommended) or pip install PyPDF2")

# Configuration
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "parsed_output"
SKIP_DIRS = {'venv', 'node_modules', '__pycache__', '.git', 'media', 'parsed_output'}
SKIP_EXTENSIONS = {'.mp3', '.wav', '.png', '.jpg', '.jpeg', '.gif', '.webp', '.mp4'}

# Category mapping based on folder names
CATEGORY_MAP = {
    '01_LUM_GAME_CONCEPTS': 'game_design',
    '02_DESIGN_LANGUAGES': 'design_language',
    '03_AI_INTELLIGENCE': 'ai_systems',
    '04_CORE_COSMOLOGY': 'metaphysics',
    '05_GENERAL_WORLDLORE': 'worldbuilding',
    '06_RITUALS_MYTHOLOGY': 'mythology_personal',
    '07_RAW_NOTES': 'raw_notes',
    '08_EXTERNAL_REFERENCES': 'references',
    '09_NEEDS_REVIEW': 'uncategorized',
    'Archetypal Context': 'archetypes'
}

# Content type patterns for classification
CONTENT_TYPE_PATTERNS = {
    'framework': [r'framework', r'model', r'system', r'architecture', r'engine', r'principles'],
    'narrative': [r'story', r'tale', r'prologue', r'act\s+[IVX]+', r'chapter', r'myth'],
    'specification': [r'specification', r'spec', r'requirements', r'implementation'],
    'design_language': [r'design language', r'lexicon', r'vocabulary', r'style guide'],
    'prompt': [r'prompt', r'instruction', r'directive'],
    'theoretical': [r'theory', r'hypothesis', r'proposal', r'exploration', r'conjecture'],
    'guide': [r'guide', r'manual', r'handbook', r'tutorial', r'how to'],
    'ritual': [r'ritual', r'ceremony', r'meditation', r'prayer', r'practice'],
    'worldbuilding': [r'world', r'realm', r'civilization', r'culture', r'geography'],
    'character': [r'character', r'persona', r'archetype', r'entity'],
    'chatlog': [r'chat', r'log', r'conversation', r'dialogue']
}

# Key concept terms to extract
CONCEPT_TERMS = [
    # Core concepts from your documents
    'miroglyph', 'hedawnism', 'sphereagonal', 'resonance', 'harmonic',
    'fractal', 'emergence', 'coherence', 'synergy', 'infinite',
    # Glyphs and symbols
    'dyajin', 'signalum', 'reflexion', 'synthru', 'aelion', 'vireon',
    'glyph', 'symbol', 'sigil', 'rune',
    # Arcs and paths
    'shadow', 'mirror', 'mythogenesis', 'initiation', 'encounter',
    'crisis', 'harmony', 'wisdom', 'integration',
    # Archetypes
    'architect', 'creator', 'oracle', 'philosopher', 'weaver', 'conductor',
    'pilgrim', 'seeker', 'guardian', 'trickster',
    # Metaphysical
    'hermetic', 'mentalism', 'correspondence', 'vibration', 'polarity',
    'rhythm', 'causation', 'gender', 'duality', 'unity',
    # Systems
    'adaptive', 'recursive', 'dynamic', 'iterative', 'cyclic',
    'equilibrium', 'threshold', 'transformation', 'transcendence',
    # Game/Design
    'lüm', 'lum', 'temple', 'schematic', 'essence', 'node',
    'resonant', 'mythOS', 'reflecture', 'schemataform',
    # Worlds
    'aeloria', 'auralis', 'echoria', 'talavora', 'xylos'
]

class DocumentConverter:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.output_dir = OUTPUT_DIR
        self.documents: List[Dict[str, Any]] = []
        self.concept_index: Dict[str, List[str]] = defaultdict(list)
        self.cross_references: Dict[str, Set[str]] = defaultdict(set)

    def run(self):
        """Main execution flow."""
        print("=" * 60)
        print("Document Conversion Process")
        print("=" * 60)

        # Create output directory
        self.output_dir.mkdir(exist_ok=True)

        # Collect all documents
        print("\n[1/5] Scanning for documents...")
        doc_paths = self._collect_documents()
        print(f"    Found {len(doc_paths)} documents")

        # Process each document
        print("\n[2/5] Processing documents...")
        for i, path in enumerate(doc_paths, 1):
            if i % 50 == 0:
                print(f"    Processed {i}/{len(doc_paths)} documents...")
            self._process_document(path)
        print(f"    Processed {len(self.documents)} documents successfully")

        # Build cross-references
        print("\n[3/5] Building cross-references...")
        self._build_cross_references()

        # Classify document quality/development stage
        print("\n[4/5] Classifying document maturity...")
        self._classify_maturity()

        # Save outputs
        print("\n[5/5] Saving outputs...")
        self._save_outputs()

        print("\n" + "=" * 60)
        print("Conversion Complete!")
        print("=" * 60)
        self._print_summary()

    def _collect_documents(self) -> List[Path]:
        """Collect all processable document paths."""
        doc_paths = []

        for root, dirs, files in os.walk(self.base_dir):
            # Skip unwanted directories
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]

            for file in files:
                path = Path(root) / file
                ext = path.suffix.lower()

                if ext in SKIP_EXTENSIONS:
                    continue

                if ext in ['.txt', '.docx', '.pdf']:
                    # Skip Python package files
                    if 'site-packages' in str(path) or 'dist-info' in str(path):
                        continue
                    doc_paths.append(path)

        return doc_paths

    def _process_document(self, path: Path):
        """Process a single document and extract structured data."""
        try:
            # Extract text content
            content = self._extract_content(path)
            if not content or len(content.strip()) < 50:
                return  # Skip empty or very short files

            # Generate document ID
            doc_id = self._generate_id(path)

            # Determine category
            category = self._determine_category(path)

            # Determine content type
            content_type = self._determine_content_type(path.name, content)

            # Extract metadata
            metadata = self._extract_metadata(path, content)

            # Extract concepts
            concepts = self._extract_concepts(content)

            # Extract structure
            structure = self._extract_structure(content)

            # Build document record
            doc = {
                'id': doc_id,
                'filename': path.name,
                'path': str(path.relative_to(self.base_dir)),
                'category': category,
                'content_type': content_type,
                'metadata': metadata,
                'concepts': concepts,
                'structure': structure,
                'content': content,
                'word_count': len(content.split()),
                'char_count': len(content)
            }

            self.documents.append(doc)

            # Update concept index
            for concept in concepts:
                self.concept_index[concept].append(doc_id)

        except Exception as e:
            print(f"    Error processing {path.name}: {e}")

    def _extract_content(self, path: Path) -> str:
        """Extract text content from document."""
        ext = path.suffix.lower()

        if ext == '.txt':
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read()
            except UnicodeDecodeError:
                with open(path, 'r', encoding='latin-1') as f:
                    return f.read()

        elif ext == '.docx' and DOCX_AVAILABLE:
            doc = Document(path)
            paragraphs = [p.text for p in doc.paragraphs]
            return '\n'.join(paragraphs)

        elif ext == '.pdf' and PDF_AVAILABLE:
            return self._extract_pdf_content(path)

        return ""

    def _extract_pdf_content(self, path: Path) -> str:
        """Extract text content from PDF file."""
        try:
            if PDF_LIB == 'pymupdf':
                doc = fitz.open(path)
                text_parts = []
                for page in doc:
                    text_parts.append(page.get_text())
                doc.close()
                return '\n'.join(text_parts)
            elif PDF_LIB == 'pypdf2':
                reader = PdfReader(path)
                text_parts = []
                for page in reader.pages:
                    text = page.extract_text()
                    if text:
                        text_parts.append(text)
                return '\n'.join(text_parts)
        except Exception as e:
            print(f"    Error extracting PDF {path.name}: {e}")
        return ""

    def _generate_id(self, path: Path) -> str:
        """Generate unique document ID."""
        rel_path = str(path.relative_to(self.base_dir))
        return hashlib.md5(rel_path.encode()).hexdigest()[:12]

    def _determine_category(self, path: Path) -> str:
        """Determine document category from path."""
        rel_path = str(path.relative_to(self.base_dir))

        for folder_prefix, category in CATEGORY_MAP.items():
            if folder_prefix in rel_path:
                return category

        return 'uncategorized'

    def _determine_content_type(self, filename: str, content: str) -> str:
        """Determine content type from filename and content."""
        text_lower = (filename + ' ' + content[:2000]).lower()

        scores = {}
        for content_type, patterns in CONTENT_TYPE_PATTERNS.items():
            score = sum(1 for p in patterns if re.search(p, text_lower))
            if score > 0:
                scores[content_type] = score

        if scores:
            return max(scores, key=scores.get)
        return 'general'

    def _extract_metadata(self, path: Path, content: str) -> Dict[str, Any]:
        """Extract metadata from document."""
        stat = path.stat()

        # Try to extract title from content
        title = self._extract_title(path.name, content)

        return {
            'title': title,
            'file_size': stat.st_size,
            'modified_date': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created_date': datetime.fromtimestamp(stat.st_ctime).isoformat(),
        }

    def _extract_title(self, filename: str, content: str) -> str:
        """Extract or generate document title."""
        # Try first non-empty line
        lines = [l.strip() for l in content.split('\n') if l.strip()]
        if lines:
            first_line = lines[0]
            # Check if it looks like a title (not too long, no special formatting)
            if len(first_line) < 100 and not first_line.startswith(('-', '*', '•', '1.')):
                return first_line

        # Fall back to filename
        return Path(filename).stem.replace('_', ' ').replace('-', ' ')

    def _extract_concepts(self, content: str) -> List[str]:
        """Extract key concepts found in content."""
        content_lower = content.lower()
        found = []

        for concept in CONCEPT_TERMS:
            if concept.lower() in content_lower:
                found.append(concept)

        return found

    def _extract_structure(self, content: str) -> Dict[str, Any]:
        """Extract document structure (headings, sections)."""
        lines = content.split('\n')

        sections = []
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Detect potential headings
            # Numbered sections: "1. Something" or "I. Something"
            if re.match(r'^[0-9]+\.\s+[A-Z]', line) or re.match(r'^[IVX]+\.\s+[A-Z]', line):
                if current_section:
                    sections.append(current_section)
                current_section = {'heading': line, 'level': 1}
            # Subsections: "1.1 Something" or bullet points as headers
            elif re.match(r'^[0-9]+\.[0-9]+\s+[A-Z]', line):
                if current_section:
                    sections.append(current_section)
                current_section = {'heading': line, 'level': 2}
            # All caps headings
            elif line.isupper() and len(line) > 3 and len(line) < 80:
                if current_section:
                    sections.append(current_section)
                current_section = {'heading': line, 'level': 1}

        if current_section:
            sections.append(current_section)

        return {
            'sections': sections,
            'section_count': len(sections),
            'has_clear_structure': len(sections) > 2
        }

    def _build_cross_references(self):
        """Build cross-reference map between documents."""
        # Create lookup for quick concept matching
        doc_concepts = {doc['id']: set(doc['concepts']) for doc in self.documents}
        doc_names = {doc['id']: doc['filename'].lower() for doc in self.documents}

        for doc in self.documents:
            doc_id = doc['id']

            # Find documents with shared concepts (minimum 3 shared)
            my_concepts = doc_concepts[doc_id]

            for other_doc in self.documents:
                other_id = other_doc['id']
                if other_id == doc_id:
                    continue

                shared = my_concepts & doc_concepts[other_id]
                if len(shared) >= 3:
                    self.cross_references[doc_id].add(other_id)

        # Add cross-references to documents
        for doc in self.documents:
            doc['related_documents'] = list(self.cross_references.get(doc['id'], []))

    def _classify_maturity(self):
        """Classify document maturity/development stage."""
        for doc in self.documents:
            score = 0
            content = doc['content'].lower()

            # Positive indicators (developed ideas)
            if doc['structure']['has_clear_structure']:
                score += 2
            if doc['word_count'] > 1000:
                score += 1
            if doc['word_count'] > 3000:
                score += 1
            if len(doc['concepts']) > 5:
                score += 1
            if doc['content_type'] in ['framework', 'specification', 'guide']:
                score += 1

            # Negative indicators (sketchy/raw)
            if 'todo' in content or 'tbd' in content or '???' in content:
                score -= 1
            if doc['content_type'] in ['chatlog', 'raw_notes']:
                score -= 2
            if doc['category'] == 'raw_notes':
                score -= 1
            if 'draft' in doc['filename'].lower():
                score -= 1
            if doc['word_count'] < 300:
                score -= 1

            # Classify
            if score >= 3:
                maturity = 'developed'
            elif score >= 1:
                maturity = 'emerging'
            elif score >= -1:
                maturity = 'sketch'
            else:
                maturity = 'raw'

            doc['maturity'] = maturity
            doc['maturity_score'] = score

    def _save_outputs(self):
        """Save all outputs to files."""
        # 1. Save individual document JSONs by category
        by_category = defaultdict(list)
        for doc in self.documents:
            by_category[doc['category']].append(doc)

        for category, docs in by_category.items():
            cat_dir = self.output_dir / category
            cat_dir.mkdir(exist_ok=True)

            # Save category index
            index = [{
                'id': d['id'],
                'filename': d['filename'],
                'title': d['metadata']['title'],
                'content_type': d['content_type'],
                'maturity': d['maturity'],
                'word_count': d['word_count'],
                'concepts': d['concepts']
            } for d in docs]

            with open(cat_dir / '_index.json', 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)

            # Save full documents
            for doc in docs:
                safe_name = re.sub(r'[<>:"/\\|?*]', '_', Path(doc['filename']).stem)
                with open(cat_dir / f"{safe_name}.json", 'w', encoding='utf-8') as f:
                    json.dump(doc, f, indent=2, ensure_ascii=False)

        # 2. Save master index
        master_index = {
            'generated': datetime.now().isoformat(),
            'total_documents': len(self.documents),
            'by_category': {cat: len(docs) for cat, docs in by_category.items()},
            'by_maturity': self._count_by_field('maturity'),
            'by_content_type': self._count_by_field('content_type'),
            'documents': [{
                'id': d['id'],
                'filename': d['filename'],
                'path': d['path'],
                'title': d['metadata']['title'],
                'category': d['category'],
                'content_type': d['content_type'],
                'maturity': d['maturity'],
                'word_count': d['word_count'],
                'concepts': d['concepts'],
                'related_documents': d['related_documents']
            } for d in self.documents]
        }

        with open(self.output_dir / 'master_index.json', 'w', encoding='utf-8') as f:
            json.dump(master_index, f, indent=2, ensure_ascii=False)

        # 3. Save concept index
        concept_data = {
            concept: {
                'count': len(doc_ids),
                'documents': doc_ids
            }
            for concept, doc_ids in sorted(self.concept_index.items(), key=lambda x: -len(x[1]))
        }

        with open(self.output_dir / 'concept_index.json', 'w', encoding='utf-8') as f:
            json.dump(concept_data, f, indent=2, ensure_ascii=False)

        # 4. Save relationship graph
        graph = {
            'nodes': [{'id': d['id'], 'label': d['metadata']['title'][:50], 'category': d['category']}
                      for d in self.documents],
            'edges': []
        }

        seen_edges = set()
        for doc_id, related in self.cross_references.items():
            for rel_id in related:
                edge_key = tuple(sorted([doc_id, rel_id]))
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    graph['edges'].append({'source': doc_id, 'target': rel_id})

        with open(self.output_dir / 'relationship_graph.json', 'w', encoding='utf-8') as f:
            json.dump(graph, f, indent=2, ensure_ascii=False)

        # 5. Save analysis summary (human readable)
        self._save_analysis_summary()

    def _count_by_field(self, field: str) -> Dict[str, int]:
        """Count documents by a specific field."""
        counts = defaultdict(int)
        for doc in self.documents:
            counts[doc[field]] += 1
        return dict(counts)

    def _save_analysis_summary(self):
        """Save human-readable analysis summary."""
        lines = []
        lines.append("=" * 70)
        lines.append("DOCUMENT ANALYSIS SUMMARY")
        lines.append("=" * 70)
        lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Total Documents Processed: {len(self.documents)}")

        # By category
        lines.append("\n" + "-" * 40)
        lines.append("DOCUMENTS BY CATEGORY")
        lines.append("-" * 40)
        by_cat = self._count_by_field('category')
        for cat, count in sorted(by_cat.items(), key=lambda x: -x[1]):
            lines.append(f"  {cat}: {count}")

        # By maturity
        lines.append("\n" + "-" * 40)
        lines.append("DOCUMENTS BY MATURITY")
        lines.append("-" * 40)
        by_mat = self._count_by_field('maturity')
        for mat in ['developed', 'emerging', 'sketch', 'raw']:
            count = by_mat.get(mat, 0)
            lines.append(f"  {mat}: {count}")

        # Top concepts
        lines.append("\n" + "-" * 40)
        lines.append("TOP 30 CONCEPTS (by document count)")
        lines.append("-" * 40)
        sorted_concepts = sorted(self.concept_index.items(), key=lambda x: -len(x[1]))[:30]
        for concept, doc_ids in sorted_concepts:
            lines.append(f"  {concept}: {len(doc_ids)} documents")

        # Developed documents (ready for deeper work)
        lines.append("\n" + "-" * 40)
        lines.append("DEVELOPED DOCUMENTS (solid ideas)")
        lines.append("-" * 40)
        developed = [d for d in self.documents if d['maturity'] == 'developed']
        for doc in sorted(developed, key=lambda x: -x['word_count'])[:30]:
            lines.append(f"  [{doc['category']}] {doc['metadata']['title'][:50]}")
            lines.append(f"      {doc['word_count']} words | {doc['content_type']} | {len(doc['concepts'])} concepts")

        # Highly connected documents
        lines.append("\n" + "-" * 40)
        lines.append("MOST CONNECTED DOCUMENTS")
        lines.append("-" * 40)
        for doc in sorted(self.documents, key=lambda x: -len(x['related_documents']))[:15]:
            if doc['related_documents']:
                lines.append(f"  {doc['metadata']['title'][:45]}: {len(doc['related_documents'])} connections")

        # Save
        with open(self.output_dir / 'analysis_summary.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _print_summary(self):
        """Print summary to console."""
        print(f"\nOutput Location: {self.output_dir}")
        print(f"\nDocuments Processed: {len(self.documents)}")

        by_mat = self._count_by_field('maturity')
        print("\nBy Maturity:")
        for mat in ['developed', 'emerging', 'sketch', 'raw']:
            print(f"  - {mat}: {by_mat.get(mat, 0)}")

        print("\nOutput Files:")
        print("  - master_index.json (main document index)")
        print("  - concept_index.json (concept-to-document mapping)")
        print("  - relationship_graph.json (document connections)")
        print("  - analysis_summary.txt (human-readable summary)")
        print("  - [category]/_index.json (per-category indices)")
        print("  - [category]/[document].json (full document data)")


if __name__ == '__main__':
    converter = DocumentConverter(BASE_DIR)
    converter.run()
