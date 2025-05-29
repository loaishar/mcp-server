# 📚 Examples Directory

This directory contains practical examples and templates for using the MCP server in various scenarios.

## 📁 Directory Structure

```
examples/
├── browser-automation/    # Browser automation examples
├── custom-tools/         # Custom tool implementations
└── README.md            # This file
```

## 🎯 Available Examples

### 🌐 **Browser Automation** (`browser-automation/`)
Examples demonstrating browser automation capabilities using Playwright and other tools.

**Contents:**
- Web scraping examples
- UI testing scenarios
- Page interaction patterns
- Screenshot and PDF generation

### 🔧 **Custom Tools** (`custom-tools/`)
Templates and examples for creating custom MCP tools.

**Contents:**
- Tool implementation patterns
- Input schema definitions
- Error handling examples
- Integration patterns

## 🚀 Getting Started

### **Prerequisites**
Before running examples, ensure you have:
1. MCP server properly configured
2. Required dependencies installed
3. Environment variables set

### **Running Examples**
Each example directory contains:
- `README.md` - Specific instructions
- `requirements.txt` - Python dependencies (if applicable)
- `package.json` - Node.js dependencies (if applicable)
- Example scripts and configurations

### **Basic Usage**
```bash
# Navigate to an example directory
cd examples/browser-automation

# Follow the README instructions
cat README.md

# Install dependencies (if needed)
pip install -r requirements.txt
# or
npm install

# Run the example
python example_script.py
# or
node example_script.js
```

## 📋 Example Categories

### **1. Browser Automation Examples**
- **Web Scraping**: Extract data from websites
- **UI Testing**: Automated testing scenarios
- **Page Interactions**: Form filling, clicking, navigation
- **Content Generation**: Screenshots, PDFs, reports

### **2. Custom Tool Examples**
- **Simple Tools**: Basic tool implementations
- **Advanced Tools**: Complex tools with multiple features
- **Integration Tools**: Tools that integrate with external services
- **Utility Tools**: Helper tools for common tasks

## 🛠️ Creating Your Own Examples

### **Example Structure**
```
your-example/
├── README.md           # Description and instructions
├── requirements.txt    # Python dependencies
├── package.json       # Node.js dependencies (if applicable)
├── config/            # Configuration files
├── src/               # Source code
└── tests/             # Test files
```

### **Best Practices**
1. **Clear Documentation**: Include comprehensive README
2. **Dependency Management**: List all dependencies
3. **Error Handling**: Include proper error handling
4. **Configuration**: Use environment variables for settings
5. **Testing**: Include test cases where applicable

### **Template Structure**
```python
#!/usr/bin/env python3
"""
Example: [Brief Description]

This example demonstrates [what it does].

Prerequisites:
- [List prerequisites]

Usage:
    python example.py [arguments]

Environment Variables:
    EXAMPLE_VAR - Description of variable
"""

import os
import sys
from typing import Dict, Any

def main():
    """Main example function."""
    try:
        # Example implementation
        print("🚀 Starting example...")
        
        # Your code here
        
        print("✅ Example completed successfully!")
        
    except Exception as e:
        print(f"❌ Example failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## 🔧 Configuration

### **Environment Variables**
Examples may use these common environment variables:
- `MCP_SERVER_URL` - MCP server endpoint
- `API_KEYS` - Various API keys for services
- `DEBUG` - Enable debug logging
- `TIMEOUT` - Request timeout settings

### **Configuration Files**
Examples may include:
- `.env.example` - Environment variable template
- `config.json` - JSON configuration
- `settings.py` - Python configuration module

## 🧪 Testing Examples

### **Running Tests**
```bash
# Run all tests in an example
cd examples/your-example
python -m pytest tests/

# Run specific test
python -m pytest tests/test_specific.py -v

# Run with coverage
python -m pytest tests/ --cov=src
```

### **Test Structure**
```python
import pytest
from src.example_module import example_function

def test_example_function():
    """Test the example function."""
    result = example_function("test_input")
    assert result == "expected_output"

def test_example_error_handling():
    """Test error handling."""
    with pytest.raises(ValueError):
        example_function(None)
```

## 📚 Learning Resources

### **Documentation Links**
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [Python MCP SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Playwright Documentation](https://playwright.dev/python/)

### **Related Guides**
- [Setup Guide](../docs/guides/SETUP.md)
- [Development Guide](../docs/guides/DEVELOPMENT.md)
- [Troubleshooting](../docs/guides/TROUBLESHOOTING.md)

## 🤝 Contributing Examples

### **Submission Guidelines**
1. **Follow Structure**: Use the standard example structure
2. **Include Tests**: Add appropriate test cases
3. **Document Thoroughly**: Comprehensive README and comments
4. **Test Locally**: Ensure examples work before submission

### **Example Ideas**
- Database integration examples
- API integration patterns
- File processing workflows
- Data analysis scenarios
- Machine learning integrations
- Cloud service integrations

## 🐛 Troubleshooting

### **Common Issues**
1. **Missing Dependencies**: Check requirements.txt/package.json
2. **Environment Variables**: Verify all required variables are set
3. **Permissions**: Ensure proper file/directory permissions
4. **Network Issues**: Check connectivity to external services

### **Getting Help**
- Check example-specific README files
- Review error messages and logs
- Consult main project documentation
- Check GitHub issues for similar problems

## 📝 Notes

- Examples are for educational purposes
- Production use may require additional security considerations
- Always review and understand code before running
- Keep examples updated with latest MCP server features
