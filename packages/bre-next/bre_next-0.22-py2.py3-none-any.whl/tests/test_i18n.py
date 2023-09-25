from bre.i18n import translate


def test_translate():
    assert translate("company_code", "de") == "Firmennummer"
    assert translate("company_code", "en") == "Company code"
    assert translate("company_code", "nl") == "Bedrijfscode"
    assert translate("company_code", "xx") == "company_code"  # Not translated
