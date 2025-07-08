# Contributing to AI Agent Simulation Platform

We love your input! We want to make contributing to the AI Agent Simulation Platform as easy and transparent as possible, whether it's:

- Reporting a bug
- Discussing the current state of the code
- Submitting a fix
- Proposing new features
- Becoming a maintainer

## Development Process

We use GitHub to host code, to track issues and feature requests, as well as accept pull requests.

### Pull Request Process

1. **Fork the repository** and create your branch from `main`
2. **Make your changes** following our coding standards
3. **Add tests** for any new functionality
4. **Update documentation** if needed
5. **Ensure the test suite passes**
6. **Submit a pull request**

### Branch Naming Convention

- `feature/agent-library-enhancement` - New features
- `fix/favorites-api-bug` - Bug fixes
- `docs/api-documentation` - Documentation updates
- `refactor/database-optimization` - Code refactoring
- `test/agent-creation-workflow` - Test improvements

## Code Standards

### Python (Backend)

```python
# Use type hints
def create_agent(agent_data: dict) -> dict:
    """Create a new agent with the provided data.
    
    Args:
        agent_data: Dictionary containing agent information
        
    Returns:
        Dictionary with created agent data
        
    Raises:
        ValueError: If agent_data is invalid
    """
    pass

# Follow PEP 8
# Use meaningful variable names
# Write comprehensive docstrings
# Handle errors appropriately
```

### JavaScript/React (Frontend)

```javascript
// Use ES6+ features
const AgentCard = ({ agent, onFavorite }) => {
  const [isFavorite, setIsFavorite] = useState(false);
  
  // Use meaningful component names
  // Implement proper error handling
  // Use React hooks appropriately
  // Follow consistent naming conventions
  
  return (
    <div className="agent-card">
      {/* Component JSX */}
    </div>
  );
};

export default AgentCard;
```

### Git Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat: add star icons to agent cards
fix: resolve favorites API authentication issue
docs: update API documentation for saved agents
style: improve agent card hover effects
refactor: optimize database queries for agent library
test: add comprehensive tests for favorites system
```

## Testing

### Running Tests

```bash
# Backend tests
cd backend
python -m pytest tests/ -v --cov=server

# Frontend tests
cd frontend
yarn test --coverage

# Integration tests
./scripts/run-integration-tests.sh
```

### Writing Tests

#### Backend Tests (pytest)
```python
import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_create_agent():
    """Test agent creation endpoint."""
    agent_data = {
        "name": "Test Agent",
        "archetype": "scientist",
        "goal": "Test goal"
    }
    
    response = client.post("/api/agents", json=agent_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Test Agent"
```

#### Frontend Tests (Jest/React Testing Library)
```javascript
import { render, screen, fireEvent } from '@testing-library/react';
import AgentCard from './AgentCard';

describe('AgentCard', () => {
  const mockAgent = {
    id: '1',
    name: 'Test Agent',
    archetype: 'scientist'
  };

  test('renders agent information', () => {
    render(<AgentCard agent={mockAgent} />);
    expect(screen.getByText('Test Agent')).toBeInTheDocument();
  });

  test('calls onFavorite when star is clicked', () => {
    const mockOnFavorite = jest.fn();
    render(<AgentCard agent={mockAgent} onFavorite={mockOnFavorite} />);
    
    fireEvent.click(screen.getByRole('button', { name: /favorite/i }));
    expect(mockOnFavorite).toHaveBeenCalledWith(mockAgent);
  });
});
```

## Documentation

### API Documentation
- Use OpenAPI/Swagger annotations
- Provide clear examples
- Document all parameters and responses
- Include error codes and messages

### Code Documentation
- Write clear, concise comments
- Document complex logic
- Use meaningful variable names
- Include usage examples

### README Updates
- Keep installation instructions current
- Update feature lists
- Add new API endpoints
- Include troubleshooting tips

## Issue Reporting

### Bug Reports

When reporting bugs, please include:

1. **Environment details**
   - Operating system
   - Python/Node.js versions
   - Browser (if frontend issue)

2. **Steps to reproduce**
   - Clear, numbered steps
   - Expected vs actual behavior
   - Screenshots if applicable

3. **Error messages**
   - Full error logs
   - Stack traces
   - Console output

### Feature Requests

For new features, please provide:

1. **Use case description**
   - Who would use this feature?
   - What problem does it solve?
   - How would it work?

2. **Implementation suggestions**
   - Possible approaches
   - Technical considerations
   - UI/UX mockups if applicable

3. **Priority and impact**
   - How important is this feature?
   - What's the expected user impact?

## Development Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- MongoDB 4.4+
- Git

### Local Development
```bash
# Clone the repository
git clone https://github.com/your-username/ai-agent-simulation.git
cd ai-agent-simulation

# Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Configure your .env file

# Set up frontend
cd ../frontend
yarn install
cp .env.example .env
# Configure your .env file

# Start development servers
# Terminal 1: Backend
cd backend && uvicorn server:app --reload

# Terminal 2: Frontend
cd frontend && yarn start
```

### Development Database
For development, use a local MongoDB instance:
```bash
# Start MongoDB
mongod

# Or use Docker
docker run -d -p 27017:27017 mongo:latest
```

## Code Review Process

### Review Checklist

- [ ] Code follows project style guidelines
- [ ] Tests are included and passing
- [ ] Documentation is updated
- [ ] No unnecessary dependencies added
- [ ] Error handling is appropriate
- [ ] Performance impact is considered
- [ ] Security implications are addressed

### Review Guidelines

1. **Be constructive** - Provide specific, actionable feedback
2. **Be respectful** - Focus on the code, not the person
3. **Be thorough** - Check functionality, style, and documentation
4. **Be timely** - Respond to reviews within 2-3 business days

## Community

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and community discussion
- **Pull Requests**: Code contributions and reviews

### Code of Conduct
We are committed to providing a welcoming and inspiring community for all. Please read our [Code of Conduct](CODE_OF_CONDUCT.md).

### Recognition
Contributors will be recognized in:
- README.md contributor section
- Release notes
- Project documentation

## Getting Help

### Documentation
- [README.md](README.md) - Project overview and setup
- [API Documentation](http://localhost:8001/docs) - Backend API reference
- [Wiki](https://github.com/your-username/ai-agent-simulation/wiki) - Detailed guides

### Support Channels
- **GitHub Issues**: Technical problems and bugs
- **GitHub Discussions**: Questions and community help
- **Email**: maintainers@ai-agent-simulation.com

### Common Issues
- **Setup Problems**: Check [Troubleshooting](README.md#-troubleshooting)
- **API Issues**: Refer to [API Documentation](README.md#-api-reference)
- **UI/UX Questions**: See [Component Documentation](docs/components.md)

---

## Thank You! 🙏

Your contributions make this project better for everyone. Whether you're fixing a bug, adding a feature, or improving documentation, every contribution is valuable and appreciated.

**Happy coding!** 🚀