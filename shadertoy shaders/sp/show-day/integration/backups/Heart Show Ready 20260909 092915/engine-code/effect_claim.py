"""Claim native opacity automation before an effect envelope starts writing."""
import urllib.request


def claim(fx, is_current, base="http://localhost:8080/api/v1"):
    """Return False for a stale effect; propagate transport failures to the caller.

    Run this blocking operation in the mutation executor. The caller owns all
    envelope and bypass changes and must check the result before applying them.
    """
    if not is_current(fx):
        return False
    pid = fx.id_opacity
    if pid is None:
        return True
    request = urllib.request.Request(
        f"{base}/parameter/by-id/{pid}/phase-source", method="DELETE")
    with urllib.request.urlopen(request, timeout=2) as response:
        response.read()
    return bool(is_current(fx) and fx.id_opacity == pid)
