# MediSearch


## flowchart
![逻辑运行图](./docs/flowchat_eng.png)

MediSearch is a medical research assistant that integrates multiple modules to provide comprehensive medical advice, academic paper searches, summarization, and visualization functionalities. It leverages language models to process user queries, fetch relevant information from various sources, and present it in an organized manner.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Modules Overview](#modules-overview)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Medical Advice Retrieval**: Fetches medical advice based on user conversation history using an AI model.
- **Academic Paper Search**: Searches for relevant papers on arXiv using extracted keywords.
- **Content Summarization**: Summarizes web content and academic papers for easier understanding.
- **Visualization**: Generates diagrams and mind maps using Mermaid syntax and converts them into images.
- **Performance Tracking**: Tracks the performance of various functions and the overall program execution time.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip package manager

### Steps

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/MediSearch.git
   ```

2. **Navigate to the project directory**

   ```bash
   cd MediSearch
   ```

3. **Create a virtual environment (optional but recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

4. **Install the required packages**

   ```bash
   pip install -r requirements.txt
   ```

5. **Install Playwright browsers**

   The application uses Playwright for rendering Mermaid diagrams. Install the necessary browsers:

   ```bash
   playwright install
   ```

6. **Set up the configuration**

   - Rename `config_template.py` to `config.py`.
   - Replace placeholders with your actual API keys and configurations.

     ```python
     # config.py
     API_KEY = "your_medisearch_api_key"
     ```

   **Note**: Keep your API keys secure and do not share them publicly.

## Usage

To run the MediSearch application, execute:

```bash
python main.py
```

### Example

In `main.py`, you can modify the `conversation_history` variable to include your query:

```python
# main.py

if __name__ == "__main__":
    start_program_timer()

    # Example conversation history
    conversation_history = [
        "What are the latest research directions in traditional Chinese herbal medicine models?"
    ]

    result = asyncio.run(MediSearch(conversation_history))
    print(result["response"])

    end_program_timer()

    print_performance_data()
```

The application will process the query and provide a detailed response, including summaries, visualizations, and references.

## Project Structure

```
MediSearch/
├── main.py
├── config.py
├── models/
│   └── custom_llm.py
├── modules/
│   ├── arxiv_search.py
│   ├── flowchat.py
│   ├── llm_handler.py
│   ├── Markdown.py
│   ├── mediator.py
│   ├── performance_tracker.py
│   ├── summarizer.py
│   └── web_scraper.py
├── docs/
│   └── diagram.jpg
├── requirements.txt
└── README.md
```

## Modules Overview

### `main.py`

The entry point of the application. It orchestrates the flow by calling various modules to process the conversation history and generate the final output.

### `config.py`

Contains configuration variables such as API keys. **Ensure you keep your API keys secure and do not share them publicly.**

### `models/custom_llm.py`

Defines a custom language model class that integrates with the OpenAI API to generate responses based on prompts.

### `modules/`

Contains various modules that handle specific tasks:

- **`arxiv_search.py`**: Handles keyword extraction from conversation history and searches for relevant papers on arXiv.
- **`flowchat.py`**: Generates diagrams and mind maps using Mermaid syntax and uploads images to a server.
- **`llm_handler.py`**: Manages prompts and responses with the language model.
- **`Markdown.py`**: Contains utility functions for rendering Markdown content and parsing Mermaid syntax.
- **`mediator.py`**: Coordinates with the `MediSearchClient` to fetch medical advice and related articles.
- **`performance_tracker.py`**: Tracks the performance of functions and the overall program execution time.
- **`summarizer.py`**: Summarizes HTML content and generates outlines based on conversation history.
- **`web_scraper.py`**: Fetches and parses web content from URLs.

## Contributing

Contributions are welcome! Please follow these steps:

1. **Fork the repository**

2. **Create a new branch**

   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**

4. **Commit your changes**

   ```bash
   git commit -m "Description of your changes"
   ```

5. **Push to the branch**

   ```bash
   git push origin feature/your-feature-name
   ```

6. **Submit a pull request**

   Provide a detailed description of your changes and any related issues.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

**Note**: Ensure that you have a `requirements.txt` file listing all the Python dependencies required for the project. Also, be cautious with any API keys or sensitive information in your configuration files; they should not be included in commits or shared publicly.