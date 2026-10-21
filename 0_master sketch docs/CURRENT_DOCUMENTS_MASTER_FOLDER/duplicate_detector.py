"""
Duplicate/Overlap Detector - Identifies documents that need consolidation
based on title similarity, content overlap, and concept clustering.
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher
from typing import Dict, List, Set, Tuple, Any
import hashlib

# Configuration
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "parsed_output"
REPORT_PATH = BASE_DIR / "consolidation_report.txt"
CLUSTERS_PATH = OUTPUT_DIR / "consolidation_clusters.json"

# Similarity thresholds
TITLE_SIMILARITY_THRESHOLD = 0.6  # 60% title similarity
CONTENT_SIMILARITY_THRESHOLD = 0.4  # 40% content similarity (for longer docs)
CONCEPT_OVERLAP_THRESHOLD = 0.7  # 70% shared concepts


class DuplicateDetector:
    def __init__(self):
        self.documents = []
        self.title_clusters = defaultdict(list)
        self.content_duplicates = []
        self.concept_clusters = defaultdict(list)
        self.version_chains = defaultdict(list)
        self.consolidation_groups = []

    def run(self):
        """Main execution flow."""
        print("=" * 60)
        print("Duplicate & Overlap Detection")
        print("=" * 60)

        # Load processed documents
        print("\n[1/6] Loading processed documents...")
        self._load_documents()
        print(f"    Loaded {len(self.documents)} documents")

        # Detect title-based duplicates
        print("\n[2/6] Detecting title-based duplicates...")
        self._detect_title_duplicates()

        # Detect version chains (v1, v2, etc.)
        print("\n[3/6] Detecting version chains...")
        self._detect_version_chains()

        # Detect content-based duplicates
        print("\n[4/6] Detecting content overlaps...")
        self._detect_content_duplicates()

        # Detect concept-based clusters
        print("\n[5/6] Detecting concept clusters...")
        self._detect_concept_clusters()

        # Build consolidation groups
        print("\n[6/6] Building consolidation recommendations...")
        self._build_consolidation_groups()

        # Save outputs
        self._save_outputs()

        print("\n" + "=" * 60)
        print("Detection Complete!")
        print("=" * 60)
        self._print_summary()

    def _load_documents(self):
        """Load all processed documents from master index."""
        index_path = OUTPUT_DIR / "master_index.json"
        with open(index_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            self.documents = data['documents']

        # Also load full content for content comparison
        self.doc_content = {}
        for doc in self.documents:
            cat_dir = OUTPUT_DIR / doc['category']
            safe_name = re.sub(r'[<>:"/\\|?*]', '_', Path(doc['filename']).stem)
            json_path = cat_dir / f"{safe_name}.json"
            if json_path.exists():
                with open(json_path, 'r', encoding='utf-8') as f:
                    full_doc = json.load(f)
                    self.doc_content[doc['id']] = full_doc.get('content', '')

    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison."""
        # Remove common prefixes/suffixes
        title = re.sub(r'^(the|a|an)\s+', '', title.lower())
        # Remove version indicators
        title = re.sub(r'\s*v?\d+(\.\d+)*\s*$', '', title)
        title = re.sub(r'\s*\(?\d+\)?\s*$', '', title)
        # Remove date patterns
        title = re.sub(r'\s*\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\s*', '', title)
        # Remove special characters
        title = re.sub(r'[^a-z0-9\s]', ' ', title)
        # Collapse whitespace
        title = re.sub(r'\s+', ' ', title).strip()
        return title

    def _extract_base_name(self, filename: str) -> str:
        """Extract base name without version/date suffixes."""
        name = Path(filename).stem
        # Remove version patterns
        name = re.sub(r'[\s_-]*v?\d+(\.\d+)*$', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[\s_-]*\(\d+\)$', '', name)
        # Remove date patterns
        name = re.sub(r'[\s_-]*\d{1,2}[-_]\d{1,2}[-_]\d{2,4}$', '', name)
        # Remove common suffixes
        name = re.sub(r'[\s_-]*(copy|final|draft|old|new|updated|revised)$', '', name, flags=re.IGNORECASE)
        return name.lower().strip()

    def _string_similarity(self, s1: str, s2: str) -> float:
        """Calculate string similarity ratio."""
        return SequenceMatcher(None, s1, s2).ratio()

    def _detect_title_duplicates(self):
        """Group documents by similar titles."""
        # First pass: exact normalized title matches
        normalized_groups = defaultdict(list)
        for doc in self.documents:
            norm_title = self._normalize_title(doc['title'])
            if len(norm_title) > 3:  # Skip very short titles
                normalized_groups[norm_title].append(doc)

        # Add exact matches to clusters
        for norm_title, docs in normalized_groups.items():
            if len(docs) > 1:
                self.title_clusters[norm_title] = docs

        # Second pass: fuzzy title matching
        processed = set()
        for i, doc1 in enumerate(self.documents):
            if doc1['id'] in processed:
                continue

            norm1 = self._normalize_title(doc1['title'])
            if len(norm1) < 5:
                continue

            cluster = [doc1]
            for doc2 in self.documents[i+1:]:
                if doc2['id'] in processed:
                    continue

                norm2 = self._normalize_title(doc2['title'])
                if len(norm2) < 5:
                    continue

                sim = self._string_similarity(norm1, norm2)
                if sim >= TITLE_SIMILARITY_THRESHOLD:
                    cluster.append(doc2)
                    processed.add(doc2['id'])

            if len(cluster) > 1:
                key = norm1[:50]
                if key not in self.title_clusters:
                    self.title_clusters[key] = cluster
                    processed.add(doc1['id'])

        print(f"    Found {len(self.title_clusters)} title-based duplicate groups")

    def _detect_version_chains(self):
        """Detect documents that are versions of each other (v1, v2, etc.)."""
        # Group by base filename
        base_groups = defaultdict(list)
        for doc in self.documents:
            base = self._extract_base_name(doc['filename'])
            if len(base) > 3:
                base_groups[base].append(doc)

        # Filter to groups with multiple versions
        for base, docs in base_groups.items():
            if len(docs) > 1:
                # Sort by filename to get version order
                docs_sorted = sorted(docs, key=lambda d: d['filename'])
                self.version_chains[base] = docs_sorted

        print(f"    Found {len(self.version_chains)} version chains")

    def _get_content_fingerprint(self, content: str, chunk_size: int = 100) -> Set[str]:
        """Generate content fingerprints for comparison."""
        # Clean content
        content = re.sub(r'\s+', ' ', content.lower())
        words = content.split()

        # Create overlapping chunks
        fingerprints = set()
        for i in range(0, len(words) - chunk_size, chunk_size // 2):
            chunk = ' '.join(words[i:i + chunk_size])
            fp = hashlib.md5(chunk.encode()).hexdigest()[:8]
            fingerprints.append(fp)

        return set(fingerprints) if fingerprints else set()

    def _detect_content_duplicates(self):
        """Detect documents with significant content overlap."""
        # Only compare documents in same category or with shared concepts
        # to avoid O(n^2) comparison of all documents

        # Group by category for comparison
        by_category = defaultdict(list)
        for doc in self.documents:
            by_category[doc['category']].append(doc)

        duplicates_found = []

        for category, docs in by_category.items():
            if len(docs) < 2:
                continue

            # Compare within category
            for i, doc1 in enumerate(docs):
                content1 = self.doc_content.get(doc1['id'], '')
                if len(content1) < 500:  # Skip very short docs
                    continue

                words1 = set(re.findall(r'\b\w{4,}\b', content1.lower()))

                for doc2 in docs[i+1:]:
                    content2 = self.doc_content.get(doc2['id'], '')
                    if len(content2) < 500:
                        continue

                    # Quick check: word overlap
                    words2 = set(re.findall(r'\b\w{4,}\b', content2.lower()))
                    if not words1 or not words2:
                        continue

                    word_overlap = len(words1 & words2) / min(len(words1), len(words2))

                    if word_overlap > 0.5:  # High word overlap, check more carefully
                        # Sample-based content comparison
                        sample1 = content1[:2000]
                        sample2 = content2[:2000]
                        sim = self._string_similarity(sample1, sample2)

                        if sim >= CONTENT_SIMILARITY_THRESHOLD:
                            duplicates_found.append({
                                'doc1': doc1,
                                'doc2': doc2,
                                'similarity': sim,
                                'word_overlap': word_overlap
                            })

        self.content_duplicates = duplicates_found
        print(f"    Found {len(self.content_duplicates)} content-based duplicate pairs")

    def _detect_concept_clusters(self):
        """Group documents by concept overlap."""
        # Build concept sets for each document
        doc_concepts = {doc['id']: set(doc['concepts']) for doc in self.documents}

        # Find documents with high concept overlap
        processed = set()
        clusters = []

        for doc1 in self.documents:
            if doc1['id'] in processed:
                continue

            concepts1 = doc_concepts[doc1['id']]
            if len(concepts1) < 3:
                continue

            cluster = [doc1]
            for doc2 in self.documents:
                if doc2['id'] == doc1['id'] or doc2['id'] in processed:
                    continue

                concepts2 = doc_concepts[doc2['id']]
                if len(concepts2) < 3:
                    continue

                # Calculate Jaccard similarity
                intersection = len(concepts1 & concepts2)
                union = len(concepts1 | concepts2)
                if union > 0:
                    overlap = intersection / union
                    if overlap >= CONCEPT_OVERLAP_THRESHOLD:
                        cluster.append(doc2)

            if len(cluster) > 1:
                # Name cluster by common concepts
                common = set.intersection(*[doc_concepts[d['id']] for d in cluster])
                cluster_name = ', '.join(sorted(common)[:3]) if common else 'mixed'
                self.concept_clusters[cluster_name].extend(cluster)
                for d in cluster:
                    processed.add(d['id'])

        print(f"    Found {len(self.concept_clusters)} concept-based clusters")

    def _build_consolidation_groups(self):
        """Build final consolidation recommendations."""
        # Merge all detection results into unified groups
        all_groups = []
        seen_docs = set()

        # Priority 1: Version chains (clear consolidation candidates)
        for base_name, docs in self.version_chains.items():
            doc_ids = {d['id'] for d in docs}
            if doc_ids - seen_docs:  # Has unseen docs
                all_groups.append({
                    'type': 'version_chain',
                    'name': base_name,
                    'documents': docs,
                    'recommendation': 'consolidate_to_latest',
                    'priority': 'high'
                })
                seen_docs.update(doc_ids)

        # Priority 2: Title duplicates
        for title, docs in self.title_clusters.items():
            doc_ids = {d['id'] for d in docs}
            unseen = doc_ids - seen_docs
            if unseen:
                unseen_docs = [d for d in docs if d['id'] in unseen]
                if len(unseen_docs) > 1:
                    all_groups.append({
                        'type': 'title_duplicate',
                        'name': title[:50],
                        'documents': unseen_docs,
                        'recommendation': 'review_and_merge',
                        'priority': 'high'
                    })
                    seen_docs.update(unseen)

        # Priority 3: Content duplicates
        for dup in self.content_duplicates:
            doc_ids = {dup['doc1']['id'], dup['doc2']['id']}
            unseen = doc_ids - seen_docs
            if len(unseen) == 2:  # Both unseen
                all_groups.append({
                    'type': 'content_duplicate',
                    'name': f"{dup['doc1']['title'][:30]} / {dup['doc2']['title'][:30]}",
                    'documents': [dup['doc1'], dup['doc2']],
                    'similarity': dup['similarity'],
                    'recommendation': 'deduplicate',
                    'priority': 'medium'
                })
                seen_docs.update(doc_ids)

        # Priority 4: Concept clusters (potential consolidation)
        for cluster_name, docs in self.concept_clusters.items():
            doc_ids = {d['id'] for d in docs}
            unseen = doc_ids - seen_docs
            if len(unseen) >= 2:
                unseen_docs = [d for d in docs if d['id'] in unseen]
                all_groups.append({
                    'type': 'concept_cluster',
                    'name': cluster_name,
                    'documents': unseen_docs,
                    'recommendation': 'consider_consolidating',
                    'priority': 'low'
                })
                seen_docs.update(unseen)

        self.consolidation_groups = all_groups
        print(f"    Built {len(all_groups)} consolidation groups")

    def _save_outputs(self):
        """Save detection results."""
        # Save JSON data
        clusters_data = {
            'generated': str(Path(__file__).stat().st_mtime),
            'total_groups': len(self.consolidation_groups),
            'by_type': {
                'version_chains': len([g for g in self.consolidation_groups if g['type'] == 'version_chain']),
                'title_duplicates': len([g for g in self.consolidation_groups if g['type'] == 'title_duplicate']),
                'content_duplicates': len([g for g in self.consolidation_groups if g['type'] == 'content_duplicate']),
                'concept_clusters': len([g for g in self.consolidation_groups if g['type'] == 'concept_cluster']),
            },
            'groups': self.consolidation_groups
        }

        with open(CLUSTERS_PATH, 'w', encoding='utf-8') as f:
            json.dump(clusters_data, f, indent=2, ensure_ascii=False)

        # Save human-readable report
        self._save_report()

    def _save_report(self):
        """Generate human-readable consolidation report."""
        lines = []
        lines.append("=" * 80)
        lines.append("DOCUMENT CONSOLIDATION REPORT")
        lines.append("=" * 80)
        lines.append(f"\nTotal documents analyzed: {len(self.documents)}")
        lines.append(f"Consolidation groups found: {len(self.consolidation_groups)}")

        # Summary by type
        lines.append("\n" + "-" * 40)
        lines.append("SUMMARY BY TYPE")
        lines.append("-" * 40)
        type_counts = defaultdict(int)
        for g in self.consolidation_groups:
            type_counts[g['type']] += 1
        for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
            lines.append(f"  {t}: {c} groups")

        # HIGH PRIORITY: Version chains
        version_groups = [g for g in self.consolidation_groups if g['type'] == 'version_chain']
        if version_groups:
            lines.append("\n" + "=" * 80)
            lines.append("HIGH PRIORITY: VERSION CHAINS")
            lines.append("These documents appear to be different versions of the same content.")
            lines.append("Recommendation: Keep the most recent/complete version, archive others.")
            lines.append("=" * 80)

            for i, group in enumerate(version_groups, 1):
                lines.append(f"\n[{i}] {group['name']}")
                lines.append("-" * 60)
                for doc in group['documents']:
                    maturity = doc.get('maturity', 'unknown')
                    words = doc.get('word_count', 0)
                    lines.append(f"  • {doc['filename']}")
                    lines.append(f"    Category: {doc['category']} | Words: {words} | Maturity: {maturity}")
                    lines.append(f"    Path: {doc['path']}")

        # HIGH PRIORITY: Title duplicates
        title_groups = [g for g in self.consolidation_groups if g['type'] == 'title_duplicate']
        if title_groups:
            lines.append("\n" + "=" * 80)
            lines.append("HIGH PRIORITY: TITLE DUPLICATES")
            lines.append("These documents have very similar titles and likely cover the same topic.")
            lines.append("Recommendation: Review and merge into a single authoritative document.")
            lines.append("=" * 80)

            for i, group in enumerate(title_groups, 1):
                lines.append(f"\n[{i}] \"{group['name']}\"")
                lines.append("-" * 60)
                for doc in group['documents']:
                    maturity = doc.get('maturity', 'unknown')
                    words = doc.get('word_count', 0)
                    lines.append(f"  • {doc['filename']}")
                    lines.append(f"    Title: {doc['title'][:60]}")
                    lines.append(f"    Category: {doc['category']} | Words: {words} | Maturity: {maturity}")

        # MEDIUM PRIORITY: Content duplicates
        content_groups = [g for g in self.consolidation_groups if g['type'] == 'content_duplicate']
        if content_groups:
            lines.append("\n" + "=" * 80)
            lines.append("MEDIUM PRIORITY: CONTENT DUPLICATES")
            lines.append("These documents have significant content overlap.")
            lines.append("Recommendation: Review and deduplicate, keeping unique portions.")
            lines.append("=" * 80)

            for i, group in enumerate(content_groups, 1):
                sim = group.get('similarity', 0)
                lines.append(f"\n[{i}] Content similarity: {sim:.0%}")
                lines.append("-" * 60)
                for doc in group['documents']:
                    words = doc.get('word_count', 0)
                    lines.append(f"  • {doc['filename']} ({words} words)")
                    lines.append(f"    {doc['path']}")

        # LOW PRIORITY: Concept clusters
        concept_groups = [g for g in self.consolidation_groups if g['type'] == 'concept_cluster']
        if concept_groups:
            lines.append("\n" + "=" * 80)
            lines.append("LOW PRIORITY: CONCEPT CLUSTERS")
            lines.append("These documents share many concepts and may benefit from consolidation.")
            lines.append("Recommendation: Consider merging or creating a unified reference document.")
            lines.append("=" * 80)

            for i, group in enumerate(concept_groups[:20], 1):  # Limit to top 20
                lines.append(f"\n[{i}] Shared concepts: {group['name']}")
                lines.append("-" * 60)
                for doc in group['documents'][:5]:  # Limit docs shown
                    lines.append(f"  • {doc['title'][:50]}")
                    lines.append(f"    {doc['path']}")
                if len(group['documents']) > 5:
                    lines.append(f"  ... and {len(group['documents']) - 5} more documents")

        # Action items summary
        lines.append("\n" + "=" * 80)
        lines.append("RECOMMENDED ACTIONS")
        lines.append("=" * 80)
        lines.append(f"\n1. IMMEDIATE: Review {len(version_groups)} version chains")
        lines.append(f"   - Identify the most complete/recent version")
        lines.append(f"   - Archive or delete older versions")
        lines.append(f"\n2. SHORT-TERM: Merge {len(title_groups)} title duplicate groups")
        lines.append(f"   - Compare content and combine unique elements")
        lines.append(f"   - Create single authoritative documents")
        lines.append(f"\n3. ONGOING: Address {len(content_groups)} content overlaps")
        lines.append(f"   - Extract unique content from each")
        lines.append(f"   - Consolidate into coherent documents")
        lines.append(f"\n4. CONSIDER: Review {len(concept_groups)} concept clusters")
        lines.append(f"   - May benefit from unified reference documents")

        with open(REPORT_PATH, 'w', encoding='utf-8') as f:
            f.write('\n'.join(lines))

    def _print_summary(self):
        """Print summary to console."""
        print(f"\nOutputs saved to:")
        print(f"  - {REPORT_PATH}")
        print(f"  - {CLUSTERS_PATH}")

        high_priority = len([g for g in self.consolidation_groups
                           if g['priority'] == 'high'])
        print(f"\nHigh priority consolidation groups: {high_priority}")
        print(f"Total groups requiring attention: {len(self.consolidation_groups)}")


if __name__ == '__main__':
    detector = DuplicateDetector()
    detector.run()
