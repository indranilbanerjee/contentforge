"""generate-docx --c2pa-sign tells the truth about what it produced.

Found in 4.5.12: offline, the run reported `c2pa_signed: true` and nothing about whether the signature was time-stamped (PRIVACY.md says
every signature requests an RFC 3161 time-stamp), so an EU-bound file could carry an untimestamped signature with no warning. And
when the embed failed (python-docx output fails it every time: "compression method not supported: 8") the `.c2pa-tmp.docx` created for
the attempt stayed behind, empty, next to the deliverable. The result now carries `c2pa_embedded`, `c2pa_timestamped` and a `warning`
when either is false, and the temp file is removed whatever happens. A fake c2pa module stands in for the library.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

try:
    # Import everything the signing code imports BEFORE a test patches sys.modules: patch.dict removes modules first imported inside
    # its block on exit, and the next import then builds a second copy of the classes (isinstance against the first copy fails).
    from cryptography import x509  # noqa: F401
    from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID  # noqa: F401
    from cryptography.hazmat.primitives import hashes, serialization  # noqa: F401
    from cryptography.hazmat.primitives.asymmetric import ec  # noqa: F401
    HAVE_CRYPTO = True
except ImportError:
    HAVE_CRYPTO = False


def load_generator():
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("_cf_generate_docx_c2pa", SCRIPTS / "generate-docx.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def fake_c2pa(sign_file, reader_json=None):
    fake = types.ModuleType("c2pa")

    class Builder:
        def __init__(self, manifest):
            pass

        @staticmethod
        def get_supported_mime_types():
            return [DOCX_MIME]

        def set_intent(self, *a, **k):
            pass

        def sign_file(self, src, dest, signer=None):
            sign_file(src, dest)

    class Signer:
        @staticmethod
        def from_info(info):
            return object()

    class Reader:
        def __init__(self, mime, fh):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def json(self):
            return json.dumps(reader_json)

    fake.Builder, fake.Signer, fake.Reader = Builder, Signer, Reader
    fake.C2paSignerInfo = lambda **k: k
    fake.C2paBuilderIntent = types.SimpleNamespace(CREATE=1)
    fake.C2paDigitalSourceType = types.SimpleNamespace(COMPOSITE_WITH_TRAINED_ALGORITHMIC_MEDIA=2)
    return fake


@unittest.skipUnless(HAVE_CRYPTO, "cryptography is not installed here")
class TestC2paStatus(unittest.TestCase):

    def sign(self, fake):
        gd = load_generator()
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "piece.docx"
            out.write_bytes(b"PK-original")
            args = types.SimpleNamespace(c2pa_sign=True, brand="Acme", content_type="article", c2pa_signing_cert=None,
                                         c2pa_signing_key=None)
            with mock.patch.dict(sys.modules, {"c2pa": fake}):
                result = gd._maybe_c2pa_sign_docx(out, args, "A title")
            left_over = sorted(p.name for p in Path(tmp).iterdir())
            return result, left_over

    def test_a_failed_embed_says_sidecar_only_warns_and_leaves_no_temp_file(self):
        def fail(src, dest):
            Path(dest).write_bytes(b"")                 # c2pa creates the destination, then fails
            raise RuntimeError("compression method not supported: 8")

        result, left_over = self.sign(fake_c2pa(fail))
        self.assertTrue(result["c2pa_signed"], result)            # existing field, unchanged
        self.assertFalse(result["c2pa_embedded"], result)
        self.assertFalse(result["c2pa_timestamped"], result)
        self.assertIn("sidecar file, not embedded", result["warning"])
        self.assertEqual(left_over, ["piece.c2pa.json", "piece.docx"], left_over)

    def test_an_embedded_signature_without_a_timestamp_warns(self):
        def ok(src, dest):
            Path(dest).write_bytes(b"PK-signed")

        reader = {"active_manifest": "urn:uuid:1", "manifests": {"urn:uuid:1": {"signature_info": {"issuer": "ContentForge Dev"}}}}
        result, left_over = self.sign(fake_c2pa(ok, reader))
        self.assertTrue(result["c2pa_embedded"], result)
        self.assertFalse(result["c2pa_timestamped"], result)
        self.assertIn("RFC 3161", result["warning"])
        self.assertEqual(left_over, ["piece.c2pa.json", "piece.docx"], left_over)

    def test_an_embedded_timestamped_signature_has_no_warning(self):
        def ok(src, dest):
            Path(dest).write_bytes(b"PK-signed")

        reader = {"active_manifest": "urn:uuid:1",
                  "manifests": {"urn:uuid:1": {"signature_info": {"issuer": "X", "time": "2026-10-28T03:00:00+00:00"}}}}
        result, _ = self.sign(fake_c2pa(ok, reader))
        self.assertTrue(result["c2pa_embedded"] and result["c2pa_timestamped"], result)
        self.assertNotIn("warning", result)


if __name__ == "__main__":
    unittest.main()
