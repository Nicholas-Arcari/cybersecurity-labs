"""Tests for nessus_parser.py - Nessus XML report parser."""

import os
import csv
import pytest

from nessus_parser import parse_nessus, SEVERITY_MAP


# Minimal valid .nessus XML for testing
SAMPLE_NESSUS_XML = """\
<?xml version="1.0" ?>
<NessusClientData_v2>
  <Report name="Test Scan">
    <ReportHost name="192.168.0.109">
      <HostProperties>
        <tag name="operating-system">Microsoft Windows 10 Pro</tag>
      </HostProperties>
      <ReportItem port="445" protocol="tcp" severity="4"
                  pluginID="97833" pluginName="MS17-010: EternalBlue SMB RCE">
        <description>The remote host is affected by a critical SMB vulnerability.</description>
        <solution>Apply Microsoft patch MS17-010.</solution>
        <cvss3_base_score>9.8</cvss3_base_score>
        <cvss_base_score>10.0</cvss_base_score>
        <cve>CVE-2017-0144</cve>
        <exploit_available>true</exploit_available>
        <plugin_output>SMBv1 is enabled and vulnerable.</plugin_output>
      </ReportItem>
      <ReportItem port="3389" protocol="tcp" severity="2"
                  pluginID="18405" pluginName="RDP Encryption Level">
        <description>RDP encryption is set to a weak level.</description>
        <solution>Configure RDP to use stronger encryption.</solution>
        <cvss_base_score>5.0</cvss_base_score>
        <cve>N/A</cve>
        <exploit_available>false</exploit_available>
      </ReportItem>
      <ReportItem port="0" protocol="tcp" severity="0"
                  pluginID="10180" pluginName="Ping the remote host">
        <description>The remote host responded to a ping.</description>
        <solution>N/A</solution>
      </ReportItem>
    </ReportHost>
  </Report>
</NessusClientData_v2>
"""


@pytest.fixture
def nessus_file(tmp_file):
    """Create a temporary .nessus XML file."""
    return tmp_file(SAMPLE_NESSUS_XML, suffix=".nessus")


class TestParseNessus:
    """Tests for the parse_nessus function."""

    def test_parse_all_findings(self, nessus_file):
        findings = parse_nessus(nessus_file, min_severity=0)
        assert len(findings) == 3

    def test_parse_with_severity_filter(self, nessus_file):
        findings = parse_nessus(nessus_file, min_severity=2)
        assert len(findings) == 2
        assert all(f["severity_num"] >= 2 for f in findings)

    def test_parse_critical_only(self, nessus_file):
        findings = parse_nessus(nessus_file, min_severity=4)
        assert len(findings) == 1
        assert findings[0]["plugin_name"] == "MS17-010: EternalBlue SMB RCE"

    def test_findings_sorted_by_severity(self, nessus_file):
        findings = parse_nessus(nessus_file, min_severity=0)
        severities = [f["severity_num"] for f in findings]
        assert severities == sorted(severities, reverse=True)

    def test_finding_fields(self, nessus_file):
        findings = parse_nessus(nessus_file, min_severity=4)
        f = findings[0]
        assert f["host"] == "192.168.0.109"
        assert f["os"] == "Microsoft Windows 10 Pro"
        assert f["port"] == "445"
        assert f["protocol"] == "tcp"
        assert f["plugin_id"] == "97833"
        assert f["severity"] == "Critical"
        assert f["severity_num"] == 4
        assert f["cvss3_score"] == "9.8"
        assert f["cve"] == "CVE-2017-0144"
        assert f["exploit_available"] == "true"

    def test_empty_result_high_filter(self, nessus_file):
        findings = parse_nessus(nessus_file, min_severity=4)
        # Only one critical, filter above should still return it
        findings_above = [f for f in findings if f["severity_num"] > 4]
        assert len(findings_above) == 0

    def test_nonexistent_file(self):
        with pytest.raises(SystemExit):
            parse_nessus("/nonexistent/file.nessus")

    def test_invalid_xml(self, tmp_file):
        bad_xml = tmp_file("<invalid>xml<", suffix=".nessus")
        with pytest.raises(SystemExit):
            parse_nessus(bad_xml)


class TestSeverityMap:
    """Tests for severity mapping."""

    def test_all_levels_mapped(self):
        assert SEVERITY_MAP[0] == "Info"
        assert SEVERITY_MAP[1] == "Low"
        assert SEVERITY_MAP[2] == "Medium"
        assert SEVERITY_MAP[3] == "High"
        assert SEVERITY_MAP[4] == "Critical"
