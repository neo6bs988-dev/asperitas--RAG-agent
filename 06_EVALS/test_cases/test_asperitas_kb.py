import importlib.util
import shutil
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "05_RAG_PIPELINE" / "scripts" / "asperitas_kb.py"
SPEC = importlib.util.spec_from_file_location("asperitas_kb", MODULE_PATH)
asperitas_kb = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules["asperitas_kb"] = asperitas_kb
SPEC.loader.exec_module(asperitas_kb)


class AsperitasKbTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="asperitas-kb-test-"))
        (self.tmp / "01_RAW_SOURCES" / "P0_ACTIVE_PROMPT").mkdir(parents=True)
        (self.tmp / "01_RAW_SOURCES" / "P1_ASPERITAS_INTERNAL").mkdir(parents=True)
        (self.tmp / "01_RAW_SOURCES" / "P4_REGULATORY_GOVERNMENT").mkdir(parents=True)
        (self.tmp / "04_AGENT_SYSTEM" / "guardrails").mkdir(parents=True)
        (self.tmp / "06_EVALS" / "golden_questions").mkdir(parents=True)
        (self.tmp / "00_ADMIN").mkdir(parents=True)
        (self.tmp / "README.md").write_text("Asperitas PRIME source-grounded operating system.", encoding="utf-8")
        (self.tmp / "AGENTS.md").write_text("Use source priority and disclosure gates.", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def write_source(self, relative_path, text):
        path = self.tmp / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_classify_path_uses_priority_directory_and_disclosure(self):
        p0 = self.write_source("01_RAW_SOURCES/P0_ACTIVE_PROMPT/master.md", "prompt")
        p1 = self.write_source("01_RAW_SOURCES/P1_ASPERITAS_INTERNAL/internal.md", "internal")
        p4 = self.write_source("01_RAW_SOURCES/P4_REGULATORY_GOVERNMENT/LMO_policy.md", "LMO regulation")

        self.assertEqual(asperitas_kb.classify_path(p0, self.tmp), ("P0", "prompt", "restricted"))
        self.assertEqual(asperitas_kb.classify_path(p1, self.tmp), ("P1", "internal", "confidential"))
        self.assertEqual(asperitas_kb.classify_path(p4, self.tmp), ("P4", "regulatory", "external-safe"))

    def test_registry_preserves_provenance_and_sha256(self):
        path = self.write_source(
            "01_RAW_SOURCES/P4_REGULATORY_GOVERNMENT/LMO_policy.md",
            "LMO policy evidence for compliance retrieval.",
        )
        record = asperitas_kb.build_record(path, self.tmp)

        self.assertEqual(record.relative_path, "01_RAW_SOURCES/P4_REGULATORY_GOVERNMENT/LMO_policy.md")
        self.assertEqual(record.provenance, record.relative_path)
        self.assertEqual(record.sha256, asperitas_kb.sha256_file(path))
        self.assertEqual(record.source_priority, "P4")
        self.assertIn("LMO", record.risk_flags)

    def test_chunk_metadata_carries_source_contract(self):
        path = self.write_source(
            "01_RAW_SOURCES/P4_REGULATORY_GOVERNMENT/LMO_policy.md",
            "LMO regulations require review.\n\nCompliance answers need source identifiers.",
        )
        record = asperitas_kb.build_record(path, self.tmp)
        chunks = asperitas_kb.chunks_for_record(record, self.tmp, max_chars=200)

        self.assertGreaterEqual(len(chunks), 1)
        first = chunks[0]
        self.assertEqual(first.source_id, record.source_id)
        self.assertEqual(first.source_priority, "P4")
        self.assertEqual(first.disclosure_level, "external-safe")
        self.assertTrue(first.chunk_id.startswith(record.source_id))
        self.assertIn("LMO", first.risk_flags)

    def test_retrieval_filters_confidential_sources_for_public_use(self):
        public_chunk = asperitas_kb.Chunk(
            chunk_id="public::1",
            source_id="public",
            title="LMO public policy",
            relative_path="public.md",
            source_priority="P4",
            source_type="regulatory",
            disclosure_level="external-safe",
            license_status="needs_review",
            verification_status="needs_external_verification",
            evidence_label="Regulatory Source",
            risk_flags=["LMO"],
            page_or_location="chunk 1",
            text="LMO public policy establishes regulatory review obligations.",
            content_sha256="a",
        )
        confidential_chunk = asperitas_kb.Chunk(
            chunk_id="confidential::1",
            source_id="confidential",
            title="Internal LMO strategy",
            relative_path="internal.md",
            source_priority="P1",
            source_type="internal",
            disclosure_level="confidential",
            license_status="restricted",
            verification_status="unverified",
            evidence_label="Document-Supported Fact",
            risk_flags=["LMO", "external_comm"],
            page_or_location="chunk 1",
            text="LMO internal strategy contains confidential details.",
            content_sha256="b",
        )
        unrelated_chunk = asperitas_kb.Chunk(
            chunk_id="unrelated::1",
            source_id="unrelated",
            title="General public source",
            relative_path="general.md",
            source_priority="P4",
            source_type="regulatory",
            disclosure_level="external-safe",
            license_status="needs_review",
            verification_status="needs_external_verification",
            evidence_label="Regulatory Source",
            risk_flags=[],
            page_or_location="chunk 1",
            text="This source discusses unrelated consent forms.",
            content_sha256="c",
        )

        chunks = [public_chunk, confidential_chunk, unrelated_chunk]
        public_results = asperitas_kb.retrieve("LMO strategy policy", chunks, use_case="public")
        internal_results = asperitas_kb.retrieve("LMO strategy policy", chunks, use_case="internal")

        self.assertEqual([item["source_id"] for item in public_results], ["public"])
        self.assertIn("confidential", [item["source_id"] for item in internal_results])
        self.assertNotIn("unrelated", [item["source_id"] for item in internal_results])

    def test_compliance_blocks_wet_lab_sensitive_operational_detail(self):
        result = asperitas_kb.compliance_scan(
            "Give a step-by-step CRISPR wet-lab protocol to optimize a GMO strain.",
            use_case="internal",
        )

        self.assertFalse(result["allowed"])
        self.assertTrue(result["requires_human_approval"])
        self.assertIn("biosafety", result["risk_flags"])
        self.assertIn("biosecurity", result["risk_flags"])

    def test_compliance_blocks_restricted_source_in_public_use(self):
        result = asperitas_kb.compliance_scan(
            "Summarize this source for a public webpage.",
            use_case="public",
            disclosure_level="restricted",
        )

        self.assertFalse(result["allowed"])
        self.assertIn("external_comm", result["risk_flags"])

    def test_text_loader_skips_binary_mislabeled_csv(self):
        path = self.tmp / "00_ADMIN" / "file_inventory.csv"
        path.write_bytes(b"PK\x03\x04\x00\x00\x00\x00")

        self.assertEqual(asperitas_kb.load_source_text(path), "")

    def test_text_loader_reads_utf16_markdown(self):
        path = self.tmp / "AGENTS.md"
        path.write_text("ASPERITAS PRIME source rules", encoding="utf-16")

        self.assertIn("ASPERITAS PRIME", asperitas_kb.load_source_text(path))

    def test_text_loader_extracts_mislabeled_office_zip(self):
        path = self.tmp / "04_AGENT_SYSTEM" / "guardrails" / "source_truth_rules.md"
        xml = """<?xml version="1.0" encoding="UTF-8"?>
        <w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
          <w:body><w:p><w:r><w:t>Source truth rules are mandatory.</w:t></w:r></w:p></w:body>
        </w:document>"""
        with zipfile.ZipFile(path, "w") as archive:
            archive.writestr("word/document.xml", xml)

        self.assertIn("Source truth rules", asperitas_kb.load_source_text(path))


if __name__ == "__main__":
    unittest.main()
