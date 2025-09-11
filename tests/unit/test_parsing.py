import pytest
from pathlib import Path

from src.parsing.html_parser import HTMLParser
from src.parsing.speech_extractor import SpeechExtractor

# Define the path to the fixtures directory
FIXTURES_DIR = Path(__file__).parent.parent / 'fixtures'

@pytest.fixture
def sample_html_content() -> str:
    """Provides the content of the sample HTML fixture."""
    html_file = FIXTURES_DIR / 'sample_html.html'
    with open(html_file, 'r', encoding='utf-8') as f:
        return f.read()

@pytest.fixture
def parsing_rules() -> dict:
    """Provides a sample of parsing rules for testing."""
    return {
        'content_container': 'td[width="100%"][valign="top"]',
        'speech_link': 'a[href*="speech"]'
    }

class TestHTMLParser:
    def test_extract_content_area(self, sample_html_content, parsing_rules):
        parser = HTMLParser(sample_html_content, year=2010, rules_path=FIXTURES_DIR.parent.parent / 'config' / 'scraping_rules.yaml')
        # This is a bit of a hack, we should mock the rules loader
        parser.rules = parsing_rules
        content_area = parser.extract_content_area()
        assert content_area is not None
        assert content_area.name == 'td'

class TestSpeechExtractor:
    @pytest.fixture
    def content_area(self, sample_html_content, parsing_rules):
        """Provides a parsed content area for the extractor tests."""
        parser = HTMLParser(sample_html_content, year=2010, rules_path=FIXTures_DIR.parent.parent / 'config' / 'scraping_rules.yaml')
        parser.rules = parsing_rules
        return parser.extract_content_area()

    def test_extract_segments(self, content_area, parsing_rules):
        extractor = SpeechExtractor(content_area, parsing_rules)
        segments = extractor.extract_segments()
        
        assert len(segments) == 3
        assert "Otwieram posiedzenie Sejmu." in segments[0]
        assert "To jest pierwsza część mowy Marszałka." in segments[0]
        assert "To jest druga część mowy Marszałka, po pierwszym linku." in segments[1]
        assert "To jest ostatnia część mowy Marszałka." in segments[2]

    def test_extract_hyperlinks(self, content_area, parsing_rules):
        extractor = SpeechExtractor(content_area, parsing_rules)
        links = extractor.extract_hyperlinks()

        assert len(links) == 2
        assert links[0]['text'] == "Link do mowy Prezydenta"
        assert links[0]['href'] == "http://example.com/speech/1"
        assert links[1]['text'] == "Link do mowy Sekretarza"
        assert links[1]['href'] == "http://example.com/speech/2"
