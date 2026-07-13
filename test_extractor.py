import os
import sys
from unittest.mock import MagicMock

# Mock dependencies
sys.modules['markitdown'] = MagicMock()

# Test the service
from back.src.services.document_extractor import DocumentExtractorService

def test_extraction():
    service = DocumentExtractorService()
    # Mock the internal markitdown instance
    service.md = MagicMock()
    mock_result = MagicMock()
    mock_result.text_content = "# Test Document\n\nThis is a test markdown content."
    service.md.convert.return_value = mock_result

    # Create a dummy file
    test_file = "test.txt"
    with open(test_file, "w") as f:
        f.write("dummy content")
    
    result = service.extract_to_markdown(test_file)
    print(f"Result: {result}")
    
    service.cleanup_local_file(test_file)
    if not os.path.exists(test_file):
        print("Cleanup successful")

if __name__ == "__main__":
    test_extraction()
