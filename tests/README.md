# Security Plus Training Tool - Unit Tests

This directory contains comprehensive unit tests for the Security Plus Training Tool web application.

## Test Structure

The test suite is organized into the following files, each testing specific components:

### Test Files

1. **`test_quiz_service.py`** - Tests for `QuizService` class
   - `create_chapter_quiz()` method
   - `create_random_quiz()` method
   - `get_quiz_question()` method
   - `submit_quiz_answer()` method
   - `get_quiz_results()` method
   - `get_wrong_questions_review()` method
   - `cleanup_quiz_session()` method
   - `_parse_question_json_fields()` method

2. **`test_quiz_logic.py`** - Tests for `QuizSession` and `QuizManager` classes
   - `QuizSession` initialization and state management
   - Question submission and answer checking
   - Score calculation and progress tracking
   - Quiz results generation
   - `QuizManager` session management
   - Question filtering and shuffling

3. **`test_question_models.py`** - Tests for question model classes
   - `QuestionModel` base class
   - `MultipleChoiceQuestion` class
   - `TrueFalseQuestion` class
   - `FillInBlankQuestion` class
   - `ScenarioBasedQuestion` class
   - `create_question()` factory function

4. **`test_api_routes.py`** - Tests for API endpoints
   - GET `/api/questions` with various filters
   - GET `/api/questions/<question_id>`
   - GET `/api/categories`
   - GET `/api/tags`
   - GET `/api/stats`
   - Error handling and edge cases

5. **`test_app_routes.py`** - Tests for Flask application routes
   - Static page routes (home, about, contact, etc.)
   - Quiz-related routes
   - User authentication routes (login, register, logout)
   - Route registration and configuration

### Configuration Files

- **`conftest.py`** - Pytest configuration and fixtures
- **`pytest.ini`** - Pytest settings and markers
- **`requirements-test.txt`** - Testing dependencies

## Running Tests

### Prerequisites

Install the testing dependencies:

```bash
pip install -r tests/requirements-test.txt
```

### Running All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=. --cov-report=html
```

### Running Specific Test Files

```bash
# Run specific test file
pytest tests/test_quiz_service.py

# Run specific test class
pytest tests/test_quiz_service.py::TestQuizService

# Run specific test method
pytest tests/test_quiz_service.py::TestQuizService::test_create_chapter_quiz_success
```

### Running Tests by Category

```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run tests excluding slow tests
pytest -m "not slow"
```

## Test Coverage

The test suite aims to achieve comprehensive coverage of:

- **Unit Tests**: Individual methods and functions
- **Integration Tests**: Component interactions
- **Edge Cases**: Error conditions and boundary values
- **Mock Testing**: External dependencies and database interactions

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

- `mock_question_manager` - Mock database manager
- `sample_questions` - Sample question data
- `mock_quiz_session` - Mock quiz session
- `mock_quiz_manager` - Mock quiz manager
- `app` - Flask application instance
- `client` - Flask test client
- `runner` - Flask CLI test runner

## Mocking Strategy

Tests use extensive mocking to isolate units under test:

- **Database Operations**: All database interactions are mocked
- **External Services**: Third-party services are mocked
- **Time-dependent Operations**: Datetime operations are mocked where needed
- **Random Operations**: Random number generation is controlled for deterministic tests

## Test Data

Sample test data is provided through fixtures and includes:

- Multiple choice questions
- True/false questions
- Fill-in-blank questions
- Various difficulty levels and categories
- Realistic Security+ exam content

## Best Practices

The test suite follows these best practices:

1. **One Test Per Method**: Each test method focuses on testing one specific method
2. **Descriptive Names**: Test names clearly describe what is being tested
3. **Arrange-Act-Assert**: Tests follow the AAA pattern
4. **Isolation**: Tests are independent and can run in any order
5. **Mocking**: External dependencies are properly mocked
6. **Edge Cases**: Both success and failure scenarios are tested
7. **Documentation**: Tests serve as documentation for expected behavior

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

- Fast execution time
- No external dependencies
- Deterministic results
- Comprehensive error reporting

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure all tests pass
3. Maintain or improve test coverage
4. Update this README if adding new test categories

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure the project root is in the Python path
2. **Mock Issues**: Check that mocks are properly configured
3. **Flask Context**: Some tests may require Flask application context

### Debug Mode

Run tests with additional debugging:

```bash
# Run with detailed output
pytest -vvv

# Run with print statements
pytest -s

# Run single test with debugging
pytest -vvv -s tests/test_quiz_service.py::TestQuizService::test_create_chapter_quiz_success
```
