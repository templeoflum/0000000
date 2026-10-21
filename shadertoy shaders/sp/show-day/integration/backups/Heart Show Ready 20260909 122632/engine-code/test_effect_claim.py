"""Opacity takeover tests with no live Arena access."""
import unittest
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import effect_claim


class EffectClaimTests(unittest.TestCase):
    def setUp(self):
        self.fx = SimpleNamespace(id_opacity=123, id_bypass=456, bypassed=True)

    @patch.object(effect_claim.urllib.request, 'urlopen')
    def test_claim_deletes_only_opacity_phase_source(self, urlopen):
        current = MagicMock(return_value=True)
        self.assertTrue(effect_claim.claim(self.fx, current))
        request = urlopen.call_args.args[0]
        self.assertEqual(request.method, 'DELETE')
        self.assertEqual(request.full_url,
                         'http://localhost:8080/api/v1/parameter/by-id/123/phase-source')
        self.assertEqual(urlopen.call_args.kwargs, {'timeout': 2})
        self.assertEqual(current.call_count, 2)
        current.assert_called_with(self.fx)
        self.assertTrue(self.fx.bypassed)
        urlopen.assert_called_once()

    @patch.object(effect_claim.urllib.request, 'urlopen')
    def test_stale_before_request_does_not_write(self, urlopen):
        self.assertFalse(effect_claim.claim(self.fx, lambda fx: False))
        urlopen.assert_not_called()

    @patch.object(effect_claim.urllib.request, 'urlopen')
    def test_replaced_during_request_cannot_start_envelope(self, urlopen):
        self.assertFalse(effect_claim.claim(
            self.fx, MagicMock(side_effect=[True, False])))
        urlopen.assert_called_once()

    @patch.object(effect_claim.urllib.request, 'urlopen')
    def test_changed_opacity_binding_cannot_start_envelope(self, urlopen):
        def changed(*args, **kwargs):
            self.fx.id_opacity = 789
            return MagicMock()
        urlopen.side_effect = changed
        self.assertFalse(effect_claim.claim(self.fx, lambda fx: True))

    @patch.object(effect_claim.urllib.request, 'urlopen', side_effect=TimeoutError)
    def test_transport_failure_propagates(self, urlopen):
        with self.assertRaises(TimeoutError):
            effect_claim.claim(self.fx, lambda fx: True)

    @patch.object(effect_claim.urllib.request, 'urlopen')
    def test_effect_without_opacity_needs_no_claim(self, urlopen):
        self.fx.id_opacity = None
        self.assertTrue(effect_claim.claim(self.fx, lambda fx: True))
        urlopen.assert_not_called()


if __name__ == '__main__':
    unittest.main()
