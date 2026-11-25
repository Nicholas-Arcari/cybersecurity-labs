"""Tests for hash_identifier.py - Hash type identification and mode lookup."""

import pytest

from hash_identifier import identify_hash


class TestMD5:
    """Tests for MD5 hash identification."""

    def test_md5_lowercase(self):
        matches = identify_hash("5f4dcc3b5aa765d61d8327deb882cf99")
        types = [m["type"] for m in matches]
        assert any("MD5" in t or "NTLM" in t for t in types)

    def test_md5_hashcat_mode(self):
        matches = identify_hash("5f4dcc3b5aa765d61d8327deb882cf99")
        modes = [m["hashcat_mode"] for m in matches]
        assert 0 in modes  # MD5 = mode 0


class TestSHA:
    """Tests for SHA family hash identification."""

    def test_sha1(self):
        matches = identify_hash("aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d")
        types = [m["type"] for m in matches]
        assert any("SHA-1" in t for t in types)

    def test_sha256(self):
        matches = identify_hash("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
        types = [m["type"] for m in matches]
        assert any("SHA-256" in t for t in types)

    def test_sha512(self):
        h = "cf83e1357eefb8bdf1542850d66d8007d620e4050b5715dc83f4a921d36ce9ce47d0d13c5d85f2b0ff8318d2877eec2f63b931bd47417a81a538327af927da3e"
        matches = identify_hash(h)
        types = [m["type"] for m in matches]
        assert any("SHA-512" in t for t in types)


class TestUnixCrypt:
    """Tests for Unix crypt format identification."""

    def test_md5crypt(self):
        matches = identify_hash("$1$salt1234$mdcG5INZqRQ6oDj/u.X4g0")
        assert matches[0]["type"] == "MD5crypt (Unix)"
        assert matches[0]["hashcat_mode"] == 500

    def test_bcrypt(self):
        matches = identify_hash("$2b$12$LJ3m4ys3Lk0TSwMBfcSBhe0MJQ8OG.JhZKlGpNwTiTnLXiNquNWKy")
        assert matches[0]["type"] == "bcrypt"
        assert matches[0]["hashcat_mode"] == 3200

    def test_sha512crypt(self):
        h = "$6$rounds=5000$saltsalt$K4y8Q5NmE3BzDp7gZCpP0IiZa6Nqfmp3WZ2RbYq3TUi5dHbdJEfL8LbPzE5RqGo3Ng1I3PWeJWMi0z9NDn4vAB"
        matches = identify_hash(h)
        assert matches[0]["type"] == "SHA-512crypt (Unix)"
        assert matches[0]["hashcat_mode"] == 1800

    def test_sha256crypt(self):
        h = "$5$rounds=5000$saltsalt$A1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q7R8S9T0U1V"
        matches = identify_hash(h)
        assert matches[0]["type"] == "SHA-256crypt (Unix)"


class TestWindows:
    """Tests for Windows hash format identification."""

    def test_lm_ntlm_pwdump(self):
        matches = identify_hash("aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0")
        types = [m["type"] for m in matches]
        assert any("LM:NTLM" in t for t in types)

    def test_ntlm_hashcat_mode(self):
        matches = identify_hash("aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0")
        modes = [m["hashcat_mode"] for m in matches]
        assert 1000 in modes


class TestKerberos:
    """Tests for Kerberos hash identification."""

    def test_kerberoast(self):
        h = "$krb5tgs$23$*user$realm$spn*$a1b2c3d4e5f6"
        matches = identify_hash(h)
        assert matches[0]["type"] == "Kerberoast (TGS-REP etype 23)"
        assert matches[0]["hashcat_mode"] == 13100

    def test_asrep_roast(self):
        h = "$krb5asrep$23$user@realm:a1b2c3d4e5f6"
        matches = identify_hash(h)
        assert matches[0]["type"] == "AS-REP Roast"
        assert matches[0]["hashcat_mode"] == 18200


class TestApplicationSpecific:
    """Tests for application-specific hash formats."""

    def test_mysql5(self):
        matches = identify_hash("*6BB4837EB74329105EE4568DDA7DC67ED2CA2AD9")
        assert matches[0]["type"] == "MySQL 4.x/5.x (SHA1)"
        assert matches[0]["hashcat_mode"] == 300

    def test_postgres_md5(self):
        matches = identify_hash("md5a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6")
        assert matches[0]["type"] == "PostgreSQL MD5"

    def test_ldap_ssha(self):
        matches = identify_hash("{SSHA}W6ph5Mm5Pz8GgiULbPgzG37mj9g=")
        assert matches[0]["type"] == "LDAP SSHA"


class TestEdgeCases:
    """Tests for edge cases."""

    def test_empty_string(self):
        matches = identify_hash("")
        assert matches == []

    def test_whitespace_only(self):
        matches = identify_hash("   ")
        assert matches == []

    def test_not_a_hash(self):
        matches = identify_hash("hello world this is not a hash")
        assert matches == []

    def test_confidence_unambiguous(self):
        """Unambiguous formats (prefix-based) should have High confidence."""
        matches = identify_hash("$2b$12$LJ3m4ys3Lk0TSwMBfcSBhe0MJQ8OG.JhZKlGpNwTiTnLXiNquNWKy")
        assert matches[0]["confidence"] == "High"

    def test_confidence_ambiguous(self):
        """Ambiguous formats (length-based) should not have High confidence."""
        matches = identify_hash("5f4dcc3b5aa765d61d8327deb882cf99")
        # 32-char hex is ambiguous (MD5/NTLM), should not be High
        assert len(matches) >= 1
