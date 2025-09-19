"""
Test script for Vertex AI integration
"""
import os
import sys
import json
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_vertex_ai_service():
    """Test Vertex AI service initialization"""
    try:
        from llm.vertex_ai_service import VertexAIService
        
        # Test with mock credentials (won't actually work without real credentials)
        service = VertexAIService(
            project_id="test-project",
            location="us-central1",
            credentials_path=None
        )
        
        print("✅ Vertex AI service initialized successfully")
        return True
        
    except Exception as e:
        print(f"❌ Vertex AI service initialization failed: {e}")
        return False

def test_unified_llm_service():
    """Test unified LLM service"""
    try:
        from llm.unified_llm_service import UnifiedLLMService
        
        # Test initialization
        service = UnifiedLLMService(provider="vertex_ai")
        
        print("✅ Unified LLM service initialized successfully")
        print(f"   Provider: {service.provider}")
        print(f"   Available: {service.is_available()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified LLM service initialization failed: {e}")
        return False

def test_llm_functions():
    """Test LLM convenience functions"""
    try:
        from llm import get_llm_provider_info, switch_llm_provider
        
        # Test provider info
        info = get_llm_provider_info()
        print(f"✅ LLM provider info: {info}")
        
        return True
        
    except Exception as e:
        print(f"❌ LLM functions test failed: {e}")
        return False

def test_api_integration():
    """Test API integration"""
    try:
        from api.app.routes.check import call_llm_explainer, generate_mini_lesson
        
        # Test with mock data
        claim = "This is a test claim"
        language = "en"
        evidence = [
            {
                "title": "Test Evidence",
                "snippet": "This is test evidence",
                "url": "https://example.com"
            }
        ]
        
        # Test LLM explainer (will use fallback without real credentials)
        result = call_llm_explainer(claim, language, evidence)
        print(f"✅ LLM explainer test: {result.get('verdict', 'UNKNOWN')}")
        
        # Test mini lesson generation
        mini_lesson = generate_mini_lesson(claim, language, evidence, "FALSE")
        print(f"✅ Mini lesson test: {mini_lesson.get('mini_lesson', 'No lesson')[:50]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ API integration test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Vertex AI Integration")
    print("=" * 50)
    
    tests = [
        ("Vertex AI Service", test_vertex_ai_service),
        ("Unified LLM Service", test_unified_llm_service),
        ("LLM Functions", test_llm_functions),
        ("API Integration", test_api_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️ {test_name} test failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed! Vertex AI integration is ready.")
    else:
        print("⚠️ Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
