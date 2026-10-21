"""
Cleanup and Consolidation Script
- Archives obvious duplicates to _archive folder
- Consolidates related documents into unified versions
- Preserves all original content (nothing deleted)
"""

import os
import json
import shutil
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

try:
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False
    print("Warning: python-docx not installed")

try:
    import fitz
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# Configuration
BASE_DIR = Path(__file__).parent
ARCHIVE_DIR = BASE_DIR / "_archive"
CONSOLIDATED_DIR = BASE_DIR / "_consolidated"
OUTPUT_DIR = BASE_DIR / "parsed_output"


class CleanupManager:
    def __init__(self):
        self.archived_files = []
        self.consolidated_docs = []
        self.errors = []

    def run(self):
        """Main execution."""
        print("=" * 70)
        print("CLEANUP AND CONSOLIDATION")
        print("=" * 70)

        # Create directories
        ARCHIVE_DIR.mkdir(exist_ok=True)
        CONSOLIDATED_DIR.mkdir(exist_ok=True)

        # Phase 1: Archive exact duplicates
        print("\n[PHASE 1] Archiving exact duplicates...")
        self._archive_exact_duplicates()

        # Phase 2: Consolidate major clusters
        print("\n[PHASE 2] Consolidating document clusters...")
        self._consolidate_talavora()
        self._consolidate_infinite_story()
        self._consolidate_fractal_pilgrim()
        self._consolidate_sphereagonal()
        self._consolidate_design_languages()
        self._consolidate_prompting_guides()
        self._consolidate_adaptive_models()

        # Phase 3: Generate report
        print("\n[PHASE 3] Generating report...")
        self._generate_report()

        print("\n" + "=" * 70)
        print("CLEANUP COMPLETE")
        print("=" * 70)
        print(f"\nArchived {len(self.archived_files)} duplicate files to: {ARCHIVE_DIR}")
        print(f"Created {len(self.consolidated_docs)} consolidated documents in: {CONSOLIDATED_DIR}")

    def _archive_file(self, src_path: Path, reason: str):
        """Move a file to archive, preserving folder structure."""
        try:
            rel_path = src_path.relative_to(BASE_DIR)
            dest_path = ARCHIVE_DIR / rel_path

            # Create parent directories
            dest_path.parent.mkdir(parents=True, exist_ok=True)

            # Move file
            shutil.move(str(src_path), str(dest_path))

            self.archived_files.append({
                'original': str(rel_path),
                'archived_to': str(dest_path.relative_to(BASE_DIR)),
                'reason': reason
            })
            return True
        except Exception as e:
            self.errors.append(f"Failed to archive {src_path.name}: {e}")
            return False

    def _archive_exact_duplicates(self):
        """Archive files that are exact duplicates."""
        duplicates_to_archive = []

        # 1. txt/docx pairs - keep docx, archive txt
        txt_docx_pairs = [
            ("04_CORE_COSMOLOGY_METAPHYSICS_EXISTING", "E-gon.txt", "E-gon.docx"),
            ("04_CORE_COSMOLOGY_METAPHYSICS_EXISTING", "E-gon 2.txt", "E-gon 2.docx"),
            ("04_CORE_COSMOLOGY_METAPHYSICS_EXISTING", "Sphereagonal math.txt", "Sphereagonal math.docx"),
            ("04_CORE_COSMOLOGY_METAPHYSICS_EXISTING", "Sphereagonal theory.txt", "Sphereagonal theory.docx"),
        ]

        for folder, txt_file, docx_file in txt_docx_pairs:
            txt_path = BASE_DIR / folder / txt_file
            docx_path = BASE_DIR / folder / docx_file
            if txt_path.exists() and docx_path.exists():
                duplicates_to_archive.append((txt_path, "txt/docx duplicate - keeping docx"))

        # 2. (1) copies - exact duplicates from download
        copy_patterns = [
            ("06_RITUALS_MYTHOLOGY_PERSONAL_WRITINGS_EXISTING", "The Infinite Story(1).docx", "The Infinite Story.docx"),
            ("01_LUM_GAME_CONCEPTS_EXISTING/misc docs", "Dynamic resonance system(1).docx", "Dynamic resonance system.docx"),
            ("01_LUM_GAME_CONCEPTS_EXISTING/misc docs", "verbrato expansion(1).docx", "verbrato expansion.docx"),
            ("02_DESIGN_LANGUAGES_PHILOSOPHY_EXISTING", "how to build a universe for dummies(1).docx", "how to build a universe for dummies.docx"),
        ]

        for folder, copy_file, original_file in copy_patterns:
            copy_path = BASE_DIR / folder / copy_file
            original_path = BASE_DIR / folder / original_file
            if copy_path.exists() and original_path.exists():
                duplicates_to_archive.append((copy_path, "(1) copy duplicate"))

        # 3. Same file in multiple locations - keep in primary location
        cross_location_dupes = [
            # (archive_this, keep_this, reason)
            ("03_AI_INTELLIGENCE_IDEAS_EXISTING/Agent Base/Guiding Principles of Resonant Intelligence.docx",
             "03_AI_INTELLIGENCE_IDEAS_EXISTING/Guiding Principles of Resonant Intelligence.docx",
             "duplicate in subfolder"),
            ("03_AI_INTELLIGENCE_IDEAS_EXISTING/Agent Base/Historia Infinita.docx",
             "06_RITUALS_MYTHOLOGY_PERSONAL_WRITINGS_EXISTING/Historia Infinita.docx",
             "duplicate - keeping in mythology"),
            ("03_AI_INTELLIGENCE_IDEAS_EXISTING/Agent Base/Axioms, Phrases, and Guiding Principles.docx",
             "06_RITUALS_MYTHOLOGY_PERSONAL_WRITINGS_EXISTING/Axioms, Phrases, and Guiding Principles.docx",
             "duplicate - keeping in mythology"),
            ("03_AI_INTELLIGENCE_IDEAS_EXISTING/A Reflection on the Tapestry of Understanding.docx",
             "06_RITUALS_MYTHOLOGY_PERSONAL_WRITINGS_EXISTING/A Reflection on the Tapestry of Understanding.docx",
             "duplicate - keeping in mythology"),
            ("08_EXTERNAL_REFERENCES_AND_INSPIRATIONS/The Hero's Journey Framework.docx",
             "03_AI_INTELLIGENCE_IDEAS_EXISTING/Agent Base/Hero's Journey Framework.docx",
             "duplicate - keeping in agent base"),
            ("03_AI_INTELLIGENCE_IDEAS_EXISTING/Agent Base/Resonant Language Engine.docx",
             "03_AI_INTELLIGENCE_IDEAS_EXISTING/The Resonant Language Engine.docx",
             "duplicate in subfolder"),
        ]

        for archive_path, keep_path, reason in cross_location_dupes:
            archive_full = BASE_DIR / archive_path
            keep_full = BASE_DIR / keep_path
            if archive_full.exists() and keep_full.exists():
                duplicates_to_archive.append((archive_full, reason))

        # 4. Identical content files (100% match from detection)
        content_dupes = [
            ("04_CORE_COSMOLOGY_METAPHYSICS_EXISTING/The brain.docx",
             "subset of Hypothesis_ The Brain document"),
        ]

        for path, reason in content_dupes:
            full_path = BASE_DIR / path
            if full_path.exists():
                duplicates_to_archive.append((full_path, reason))

        # Execute archival
        for path, reason in duplicates_to_archive:
            if self._archive_file(path, reason):
                print(f"    Archived: {path.name}")

        print(f"    Total archived: {len(self.archived_files)} files")

    def _read_docx(self, path: Path) -> str:
        """Read content from docx file."""
        if not DOCX_AVAILABLE or not path.exists():
            return ""
        try:
            doc = Document(path)
            return '\n'.join([p.text for p in doc.paragraphs])
        except:
            return ""

    def _read_pdf(self, path: Path) -> str:
        """Read content from PDF file."""
        if not PDF_AVAILABLE or not path.exists():
            return ""
        try:
            doc = fitz.open(path)
            text = '\n'.join([page.get_text() for page in doc])
            doc.close()
            return text
        except:
            return ""

    def _create_consolidated_doc(self, title: str, sections: list, filename: str):
        """Create a consolidated docx document."""
        if not DOCX_AVAILABLE:
            print(f"    Skipping {filename} - python-docx not available")
            return

        doc = Document()

        # Title
        title_para = doc.add_heading(title, 0)
        title_para.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # Metadata
        doc.add_paragraph(f"Consolidated: {datetime.now().strftime('%Y-%m-%d')}")
        doc.add_paragraph(f"Source documents: {len(sections)}")
        doc.add_paragraph("")

        # Table of contents
        doc.add_heading("Contents", level=1)
        for i, section in enumerate(sections, 1):
            doc.add_paragraph(f"{i}. {section['title']}", style='List Number')
        doc.add_page_break()

        # Sections
        for section in sections:
            doc.add_heading(section['title'], level=1)

            if section.get('source'):
                source_para = doc.add_paragraph()
                source_para.add_run(f"Source: {section['source']}").italic = True

            if section.get('metadata'):
                meta_para = doc.add_paragraph()
                meta_para.add_run(section['metadata']).italic = True

            doc.add_paragraph("")  # Spacing

            # Content
            content = section.get('content', '')
            for para in content.split('\n'):
                if para.strip():
                    doc.add_paragraph(para.strip())

            doc.add_page_break()

        # Save
        output_path = CONSOLIDATED_DIR / filename
        doc.save(output_path)
        self.consolidated_docs.append({
            'filename': filename,
            'title': title,
            'sections': len(sections)
        })
        print(f"    Created: {filename} ({len(sections)} sections)")

    def _consolidate_talavora(self):
        """Consolidate all Talavora worldbuilding documents."""
        print("\n  Consolidating Talavora worldbuilding...")

        talavora_dir = BASE_DIR / "05_GENERAL_WORLDLORE_OTHER_PROJECTS_EXISTING" / "Talavora"
        if not talavora_dir.exists():
            print("    Talavora directory not found")
            return

        # Organize by category
        categories = {
            'foundations': ['Talavora foundations.docx', 'Talavora constants 01.docx',
                          'Talavora constants 02.docx', 'Talavora constants 03.docx',
                          'Talavora tempo.docx', 'Talavora harmonic cycle.docx',
                          'Talavora hermetic adherence.docx'],
            'culture': ['Talavora cultures.docx', 'Talavora religion.docx',
                       'Talavora religious texts.docx', 'Talavora religious figures.docx',
                       'Talavora schools.docx', 'Talavora symbology.docx'],
            'history': ['Talavora timeline.docx', 'Talavora wars.docx',
                       'Talavora legendary events.docx', 'Talavora prophecies.docx'],
            'places': ['Talavora locations.docx', 'Talavora architecture.docx', 'Sonovan.docx'],
            'people': ['Talavora figures.docx', 'Talavora artists.docx',
                      'Talavora occultists.docx', 'Talavora factions.docx'],
            'artifacts': ['Talavora artifacts.docx', 'Talavora tech.docx'],
            'philosophy': ['Talavora philosophy.docx', 'Talavora equilibrium.docx'],
            'mythology': ['Talavora expansion.docx', 'Talavora myths.docx',
                         'Talavora secret societies.docx'],
            'naming': ['Talavora naming 01.docx', 'Talavora naming 02.docx',
                      'Talavora naming 03.docx'],
            'stories': ['The dissonant path.docx', 'The dissonant path outline.docx',
                       'The last tuner.docx', 'The last tuner outline.docx',
                       'The last whisper.docx', 'The last whisper outline.docx']
        }

        sections = []

        for category, files in categories.items():
            category_content = []
            for filename in files:
                filepath = talavora_dir / filename
                if filepath.exists():
                    content = self._read_docx(filepath)
                    if content.strip():
                        category_content.append({
                            'file': filename,
                            'content': content
                        })

            if category_content:
                combined_content = ""
                for item in category_content:
                    combined_content += f"\n\n--- From: {item['file']} ---\n\n"
                    combined_content += item['content']

                sections.append({
                    'title': category.replace('_', ' ').title(),
                    'source': f"{len(category_content)} documents",
                    'content': combined_content
                })

        if sections:
            self._create_consolidated_doc(
                "Talavora: Complete Worldbuilding Compendium",
                sections,
                "Talavora_Complete_Worldbuilding.docx"
            )

    def _consolidate_infinite_story(self):
        """Consolidate The Infinite Story versions."""
        print("\n  Consolidating The Infinite Story...")

        story_dir = BASE_DIR / "06_RITUALS_MYTHOLOGY_PERSONAL_WRITINGS_EXISTING"

        versions = [
            ('The Infinite Story v1.docx', 'Version 1 (Early Draft)'),
            ('The Infinite Story.docx', 'Main Version'),
            ('The Infinite Story (with context).docx', 'With Context'),
        ]

        sections = []
        for filename, version_name in versions:
            filepath = story_dir / filename
            if filepath.exists():
                content = self._read_docx(filepath)
                if content.strip():
                    word_count = len(content.split())
                    sections.append({
                        'title': version_name,
                        'source': filename,
                        'metadata': f"Word count: {word_count}",
                        'content': content
                    })

        if sections:
            self._create_consolidated_doc(
                "The Infinite Story: All Versions",
                sections,
                "The_Infinite_Story_Complete.docx"
            )

    def _consolidate_fractal_pilgrim(self):
        """Consolidate The Fractal Pilgrim versions."""
        print("\n  Consolidating The Fractal Pilgrim...")

        base_dir = BASE_DIR / "06_RITUALS_MYTHOLOGY_PERSONAL_WRITINGS_EXISTING"
        books_dir = base_dir / "books" / "The Fractal Pilgrim"

        versions = [
            (base_dir / "The Fractal Pilgrim.docx", "Base Version"),
            (base_dir / "The Fractal Pilgrim (First Draft).docx", "First Draft"),
            (base_dir / "The Fractal Pilgrim (Second Draft).docx", "Second Draft"),
            (books_dir / "The fractal pilgrim outline.docx", "Outline v1"),
            (books_dir / "The fractal pilgrim outline 02.docx", "Outline v2"),
            (books_dir / "Book 01.docx", "Book 01"),
        ]

        sections = []
        for filepath, version_name in versions:
            if filepath.exists():
                content = self._read_docx(filepath)
                if content.strip():
                    word_count = len(content.split())
                    sections.append({
                        'title': version_name,
                        'source': filepath.name,
                        'metadata': f"Word count: {word_count}",
                        'content': content
                    })

        if sections:
            self._create_consolidated_doc(
                "The Fractal Pilgrim: All Versions & Outlines",
                sections,
                "The_Fractal_Pilgrim_Complete.docx"
            )

    def _consolidate_sphereagonal(self):
        """Consolidate Sphereagonal theory documents."""
        print("\n  Consolidating Sphereagonal theory...")

        meta_dir = BASE_DIR / "04_CORE_COSMOLOGY_METAPHYSICS_EXISTING"

        files = [
            ('Sphereagonal theory.docx', 'Core Theory'),
            ('Sphereagonal math.docx', 'Mathematical Framework'),
            ('E-gon.docx', 'E-gon Concept'),
            ('E-gon 2.docx', 'E-gon Extended'),
        ]

        sections = []
        for filename, title in files:
            filepath = meta_dir / filename
            if filepath.exists():
                content = self._read_docx(filepath)
                if content.strip():
                    sections.append({
                        'title': title,
                        'source': filename,
                        'content': content
                    })

        if sections:
            self._create_consolidated_doc(
                "Sphereagonal Theory: Complete Framework",
                sections,
                "Sphereagonal_Theory_Complete.docx"
            )

    def _consolidate_design_languages(self):
        """Consolidate design language documents."""
        print("\n  Consolidating design languages...")

        dl_dir = BASE_DIR / "02_DESIGN_LANGUAGES_PHILOSOPHY_EXISTING" / "Design languages_"

        # Main design languages
        main_files = [
            'Architectural design language.docx',
            'Interior design language.docx',
            'Exterior design language.docx',
            'Furniture design language.docx',
            'Industrial design language.docx',
            'Agricultural design language.docx',
            'Alchemical design language.docx',
            'Cuisine design language.docx',
            'Iconography design language.docx',
            'Typography design language.docx',
            'Speech design language.docx',
            'Grammatical design language.docx',
            'Leisure design language.docx',
            'Entertainment design language.docx',
            'Appliance design language.docx',
            'Systems architecture design language.docx',
        ]

        sections = []
        for filename in main_files:
            filepath = dl_dir / filename
            if filepath.exists():
                content = self._read_docx(filepath)
                if content.strip():
                    title = filename.replace(' design language.docx', '').replace('.docx', '')
                    sections.append({
                        'title': title,
                        'source': filename,
                        'content': content
                    })

        if sections:
            self._create_consolidated_doc(
                "Design Languages: Complete Reference",
                sections,
                "Design_Languages_Complete.docx"
            )

        # Personifications
        pers_dir = dl_dir / "7 personifications_"
        if pers_dir.exists():
            pers_files = [
                'The Architect design language.docx',
                'The Creator design language.docx',
                'The Oracle design language.docx',
                'The Philosopher design language.docx',
                'The Weaver design language.docx',
                'The Mirror design language.docx',
                'The Conductor design language.docx',
            ]

            sections = []
            for filename in pers_files:
                filepath = pers_dir / filename
                if filepath.exists():
                    content = self._read_docx(filepath)
                    if content.strip():
                        title = filename.replace(' design language.docx', '')
                        sections.append({
                            'title': title,
                            'source': filename,
                            'content': content
                        })

            if sections:
                self._create_consolidated_doc(
                    "The Seven Personifications: Design Languages",
                    sections,
                    "Seven_Personifications_Complete.docx"
                )

    def _consolidate_prompting_guides(self):
        """Consolidate AI prompting guides."""
        print("\n  Consolidating prompting guides...")

        ai_dir = BASE_DIR / "03_AI_INTELLIGENCE_IDEAS_EXISTING"

        guides = [
            ('Prompting DALLE3.docx', 'DALL-E 3'),
            ('Prompting Midjourney v6-1.docx', 'Midjourney v6.1'),
            ('Prompting Sora.docx', 'Sora Video'),
            ('Prompting Stable Diffusion Audio.docx', 'Stable Diffusion Audio'),
            ('Prompting Suno v4.docx', 'Suno v4 Music'),
            ('Upscale prompting.docx', 'AI Upscalers'),
        ]

        sections = []
        for filename, title in guides:
            filepath = ai_dir / filename
            if filepath.exists():
                content = self._read_docx(filepath)
                if content.strip():
                    sections.append({
                        'title': title,
                        'source': filename,
                        'content': content
                    })

        # Also check prompts subfolder
        prompts_dir = ai_dir / "prompts"
        if prompts_dir.exists():
            extra_files = [
                ('gemini.docx', 'Gemini'),
                ('Generation prompts.docx', 'Generation Prompts'),
                ('Conversation prompts.docx', 'Conversation Prompts'),
            ]
            for filename, title in extra_files:
                filepath = prompts_dir / filename
                if filepath.exists():
                    content = self._read_docx(filepath)
                    if content.strip():
                        sections.append({
                            'title': title,
                            'source': f"prompts/{filename}",
                            'content': content
                        })

        if sections:
            self._create_consolidated_doc(
                "AI Prompting Guide: Complete Reference",
                sections,
                "AI_Prompting_Guide_Complete.docx"
            )

    def _consolidate_adaptive_models(self):
        """Consolidate adaptive/coherence model documents."""
        print("\n  Consolidating adaptive models...")

        ai_dir = BASE_DIR / "03_AI_INTELLIGENCE_IDEAS_EXISTING"

        models = [
            ('The Adaptive Coherence Model.docx', 'Adaptive Coherence Model'),
            ('The Adaptive Coherence Model_ A Hermetic Framework for Collaborative Intelligent Systems.docx',
             'ACM: Hermetic Framework'),
            ('Adaptive Language model.docx', 'Adaptive Language Model'),
            ('Dynamic Language Model.docx', 'Dynamic Language Model'),
            ('The Resonant Language Engine.docx', 'Resonant Language Engine'),
            ('Symbolic Language Model.docx', 'Symbolic Language Model'),
            ('Guiding Principles of Resonant Intelligence.docx', 'Guiding Principles'),
        ]

        sections = []
        for filename, title in models:
            filepath = ai_dir / filename
            if filepath.exists():
                content = self._read_docx(filepath)
                if content.strip():
                    sections.append({
                        'title': title,
                        'source': filename,
                        'content': content
                    })

        if sections:
            self._create_consolidated_doc(
                "Adaptive Intelligence Models: Complete Framework",
                sections,
                "Adaptive_Intelligence_Models.docx"
            )

    def _generate_report(self):
        """Generate cleanup report."""
        report_path = BASE_DIR / "cleanup_report.txt"

        lines = []
        lines.append("=" * 70)
        lines.append("CLEANUP AND CONSOLIDATION REPORT")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("=" * 70)

        lines.append(f"\n\nARCHIVED FILES ({len(self.archived_files)} total)")
        lines.append("-" * 50)
        for item in self.archived_files:
            lines.append(f"\n  Original: {item['original']}")
            lines.append(f"  Reason: {item['reason']}")

        lines.append(f"\n\nCONSOLIDATED DOCUMENTS ({len(self.consolidated_docs)} total)")
        lines.append("-" * 50)
        for item in self.consolidated_docs:
            lines.append(f"\n  {item['filename']}")
            lines.append(f"  Title: {item['title']}")
            lines.append(f"  Sections: {item['sections']}")

        if self.errors:
            lines.append(f"\n\nERRORS ({len(self.errors)} total)")
            lines.append("-" * 50)
            for error in self.errors:
                lines.append(f"  - {error}")

        lines.append("\n\nNEXT STEPS")
        lines.append("-" * 50)
        lines.append("1. Review consolidated documents in _consolidated/ folder")
        lines.append("2. Archived files are in _archive/ folder (can be deleted if satisfied)")
        lines.append("3. Re-run document_converter.py to update the parsed_output index")
        lines.append("4. Consider further manual consolidation of remaining duplicates")

        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

        print(f"    Report saved to: {report_path}")


if __name__ == '__main__':
    manager = CleanupManager()
    manager.run()
