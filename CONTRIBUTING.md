# Contributing to AI Agent Simulation Platform

First off, thank you for considering contributing to the AI Agent Simulation Platform! It's people like you that make this platform such a great tool for AI research and simulation.

## 🌟 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report unacceptable behavior to [conduct@yourdomain.com](mailto:conduct@yourdomain.com).

## 🚀 How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

**Before Submitting A Bug Report:**
- Check the debugging guide for common issues
- Check the existing issues to see if the problem has already been reported

**How Do I Submit A Bug Report?**

Bugs are tracked as [GitHub issues](https://github.com/your-username/ai-agent-simulation/issues). Create an issue and provide the following information:

- **Use a clear and descriptive title** for the issue
- **Describe the exact steps which reproduce the problem**
- **Provide specific examples to demonstrate the steps**
- **Describe the behavior you observed after following the steps**
- **Explain which behavior you expected to see instead and why**
- **Include screenshots and animated GIFs** which show you following the described steps

### Suggesting Enhancements

Enhancement suggestions are tracked as [GitHub issues](https://github.com/your-username/ai-agent-simulation/issues). When creating an enhancement suggestion, please include:

- **Use a clear and descriptive title** for the issue
- **Provide a step-by-step description of the suggested enhancement**
- **Provide specific examples to demonstrate the steps**
- **Describe the current behavior and explain which behavior you expected to see instead**
- **Explain why this enhancement would be useful**

### Pull Requests

The process described here has several goals:

- Maintain the project's quality
- Fix problems that are important to users
- Engage the community in working toward the best possible AI simulation platform
- Enable a sustainable system for maintainers to review contributions

Please follow these steps to have your contribution considered by the maintainers:

1. Follow all instructions in the [template](PULL_REQUEST_TEMPLATE.md)
2. Follow the [styleguides](#styleguides)
3. After you submit your pull request, verify that all [status checks](https://help.github.com/articles/about-status-checks/) are passing

## 📋 Development Process

### Getting Started

1. **Fork the repository** and clone your fork
2. **Install dependencies** for both frontend and backend
3. **Set up your development environment** with the required tools
4. **Create a topic branch** from the main branch for your changes
5. **Make your changes** following our coding standards
6. **Test your changes** thoroughly
7. **Submit a pull request**

### Development Setup

#### Prerequisites
- Node.js 16.0+ and yarn
- Python 3.8+ and pip
- MongoDB 4.4+
- Git

#### Environment Setup
```bash
# Clone your fork
git clone https://github.com/YOUR-USERNAME/ai-agent-simulation.git
cd ai-agent-simulation

# Install backend dependencies
cd backend
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Install frontend dependencies
cd ../frontend
yarn install

# Set up environment variables
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edit the .env files with your configuration
```

#### Running Tests
```bash
# Backend tests
cd backend
python -m pytest tests/ -v

# Frontend tests
cd frontend
yarn test

# Run all tests
./scripts/run-all-tests.sh
```

## 📝 Styleguides

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally after the first line
- Consider starting the commit message with an applicable emoji:
  - 🎨 `:art:` when improving the format/structure of the code
  - 🐎 `:racehorse:` when improving performance
  - 🚱 `:non-potable_water:` when plugging memory leaks
  - 📝 `:memo:` when writing docs
  - 🐧 `:penguin:` when fixing something on Linux
  - 🍎 `:apple:` when fixing something on macOS
  - 🏁 `:checkered_flag:` when fixing something on Windows
  - 🐛 `:bug:` when fixing a bug
  - 🔥 `:fire:` when removing code or files
  - 💚 `:green_heart:` when fixing the CI build
  - ✅ `:white_check_mark:` when adding tests
  - 🔒 `:lock:` when dealing with security
  - ⬆️ `:arrow_up:` when upgrading dependencies
  - ⬇️ `:arrow_down:` when downgrading dependencies

### Python Styleguide

- Follow [PEP 8](https://pep8.org/)
- Use [Black](https://github.com/psf/black) for code formatting
- Use [isort](https://github.com/PyCQA/isort) for import sorting
- Add type hints to all function signatures
- Write docstrings for all public functions and classes
- Maximum line length is 88 characters (Black default)

#### Example:
```python
from typing import List, Optional

def create_agent(
    name: str,
    archetype: str,
    expertise: List[str],
    background: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new AI agent with specified characteristics.
    
    Args:
        name: The agent's display name
        archetype: The personality archetype (e.g., 'scientist', 'leader')
        expertise: List of expertise areas
        background: Optional background story
        
    Returns:
        Dictionary containing the created agent's information
        
    Raises:
        ValueError: If name or archetype is empty
    """
    if not name or not archetype:
        raise ValueError("Name and archetype are required")
        
    return {
        "name": name,
        "archetype": archetype,
        "expertise": expertise,
        "background": background or f"Expert in {', '.join(expertise)}",
    }
```

### JavaScript/React Styleguide

- Use [Prettier](https://prettier.io/) for code formatting
- Use [ESLint](https://eslint.org/) for linting
- Use functional components with hooks
- Use TypeScript for type safety
- Follow React best practices for performance
- Use meaningful component and variable names

#### Example:
```javascript
import React, { useState, useEffect, useCallback } from 'react';
import PropTypes from 'prop-types';

const AgentCard = ({ agent, onSelect, isSelected }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleSelect = useCallback(async () => {
    setIsLoading(true);
    try {
      await onSelect(agent.id);
    } catch (error) {
      console.error('Failed to select agent:', error);
    } finally {
      setIsLoading(false);
    }
  }, [agent.id, onSelect]);

  return (
    <div 
      className={`
        agent-card p-4 rounded-lg border transition-all duration-300
        ${isSelected ? 'border-purple-500 bg-purple-50' : 'border-gray-200 hover:border-gray-300'}
        ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}
      `}
      onClick={handleSelect}
    >
      <h3 className="font-semibold text-gray-900">{agent.name}</h3>
      <p className="text-sm text-gray-600">{agent.archetype}</p>
      <p className="text-xs text-gray-500 mt-2">{agent.expertise.join(', ')}</p>
    </div>
  );
};

AgentCard.propTypes = {
  agent: PropTypes.shape({
    id: PropTypes.string.isRequired,
    name: PropTypes.string.isRequired,
    archetype: PropTypes.string.isRequired,
    expertise: PropTypes.arrayOf(PropTypes.string).isRequired,
  }).isRequired,
  onSelect: PropTypes.func.isRequired,
  isSelected: PropTypes.bool,
};

AgentCard.defaultProps = {
  isSelected: false,
};

export default AgentCard;
```

### CSS/Tailwind Styleguide

- Use Tailwind CSS utility classes
- Create custom components for repeated patterns
- Use semantic class names for custom CSS
- Follow mobile-first responsive design
- Maintain consistent spacing and typography scales

## 🧪 Testing Guidelines

### Frontend Testing
- Write unit tests for utility functions
- Write component tests for React components
- Write integration tests for complex user flows
- Use React Testing Library for component testing
- Aim for 80%+ test coverage

### Backend Testing
- Write unit tests for all functions
- Write integration tests for API endpoints
- Write end-to-end tests for critical user flows
- Use pytest for Python testing
- Mock external dependencies
- Aim for 90%+ test coverage

### Test Structure
```python
# backend/tests/test_agents.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestAgentEndpoints:
    def test_create_agent_success(self):
        """Test successful agent creation."""
        agent_data = {
            "name": "Test Agent",
            "archetype": "scientist",
            "expertise": ["AI", "ML"],
        }
        response = client.post("/api/agents", json=agent_data)
        
        assert response.status_code == 201
        assert response.json()["name"] == "Test Agent"
        
    def test_create_agent_invalid_data(self):
        """Test agent creation with invalid data."""
        invalid_data = {"name": ""}  # Missing required fields
        response = client.post("/api/agents", json=invalid_data)
        
        assert response.status_code == 422
```

## 📚 Documentation

- Update documentation for any new features or changes
- Use clear, concise language
- Include code examples where appropriate
- Update API documentation for backend changes
- Update component documentation for frontend changes

## 🏷️ Issue and Pull Request Labels

### Issue Labels
- `bug` - Something isn't working
- `enhancement` - New feature or request
- `documentation` - Improvements or additions to documentation
- `good first issue` - Good for newcomers
- `help wanted` - Extra attention is needed
- `question` - Further information is requested

### Pull Request Labels
- `work in progress` - Pull request is not ready for review
- `needs review` - Pull request is ready for review
- `needs changes` - Pull request needs changes before merging
- `ready to merge` - Pull request has been approved and is ready to merge

## 📞 Getting Help

If you need help with anything related to contributing:

1. Check the [documentation](https://github.com/your-username/ai-agent-simulation/wiki)
2. Search [existing issues](https://github.com/your-username/ai-agent-simulation/issues)
3. Ask in [GitHub Discussions](https://github.com/your-username/ai-agent-simulation/discussions)
4. Join our [Discord community](https://discord.gg/yourinvite)
5. Email us at [dev@yourdomain.com](mailto:dev@yourdomain.com)

## 🙏 Recognition

Contributors who make significant contributions will be:
- Added to the Contributors section in the README
- Mentioned in release notes
- Invited to join the core team (for exceptional contributors)

Thank you for contributing to the AI Agent Simulation Platform! 🚀