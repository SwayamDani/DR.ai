# Dr.ai - AI-Powered Health Assistant

Dr.ai is an interactive web application that leverages OpenAI's GPT-4o model to provide health-related information and guidance to users through a modern, intuitive chat interface.

![Dr.ai Interface](https://via.placeholder.com/800x450)

## Features

- **Interactive Chat Interface**: Clean, modern UI with real-time responses
- **Smart Suggestions**: Dynamic generation of related questions based on conversation context
- **Persistent Conversations**: Chat history maintained throughout the session
- **New Chat Creation**: Easily start fresh conversations with a single click
- **Responsive Design**: Works seamlessly across devices

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **AI Integration**: OpenAI GPT-4o via Assistants API
- **Environment Management**: Poetry for dependency handling

## Prerequisites

- Python 3.10 or 3.11
- OpenAI API key
- Assistant ID from OpenAI

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/tannicflux/DR.ai.git
   cd DR.ai
   ```

2. **Set up environment variables**:
   Create a `.env` file in the project root with:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ASSISTANT_KEY=your_assistant_id_here
   ```

3. **Install dependencies**:
   
   Using Poetry (recommended):
   ```bash
   poetry install
   ```
   
   Using pip:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the Flask application**:
   ```bash
   flask run
   ```
   
   Or with Poetry:
   ```bash
   poetry run flask run
   ```

2. **Access the application**:
   Open your web browser and navigate to `http://127.0.0.1:5000/`

3. **Interact with Dr.ai**:
   - Type your health-related questions in the message box
   - Click suggested prompts to quickly navigate common queries
   - Start a new chat session anytime with the "Start New Chat" button

## Customization

### Modifying the Assistant

You can customize the assistant's behavior by editing the instructions in `app.py`:

```python
assistant = client.beta.assistants.create(
  name="DR.ai",
  instructions="Your custom instructions here",
  tools=[{"type": "code_interpreter"}],
  model="gpt-4o",
)
```

### Styling

The application uses a modern dark theme by default. To customize the appearance, modify `static/chat.css`.

## Deployment

For production deployment, consider:

1. Using Gunicorn as a WSGI server
2. Setting up with Nginx as a reverse proxy
3. Deploying on cloud platforms like Heroku, AWS, or Google Cloud

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [OpenAI](https://openai.com/) for providing the GPT-4o model and Assistants API
- [Flask](https://flask.palletsprojects.com/) for the web framework
- [Streamlit](https://streamlit.io/) for inspiration on interactive UI components

---

Created by [Swayam Dani & Arjun M]
