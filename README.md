# Discord AI Chatbot

This is a Discord bot powered by the Together API for AI-powered chat responses. It maintains a chat history, supports chat backups, and operates within allowed channels.

## Features
- Uses AI to respond to messages
- Maintains and manages chat history
- Supports chat backup and restore
- Restricts bot interaction to specific channels
- Provides admin commands to clear or restore chat history

## Requirements
- Python 3.8+
- `discord.py` for Discord bot interaction
- `together` for AI chat functionality
- `python-dotenv` for managing environment variables

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/DragoonT/discord-bot
   cd discord-bot
   ```

2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Create a `.env` file in the project directory and add the following:
   ```env
   DISCORD_BOT_TOKEN=your_discord_bot_token_here
   TOGETHER_API_KEY=your_together_api_key_here
   TOGETHER_MODEL_NAME=your_ai_model  # Optional, default set in code
   ```

## Usage

Run the bot using:
```sh
python bot.py
```

### Bot Commands
- `!clean` - Clears the chat history
- `!restore` - Restores chat history from backup
- `!save` - Saves the current chat history as a backup

### Environment Variables
- `DISCORD_BOT_TOKEN`: Your Discord bot token
- `TOGETHER_API_KEY`: API key for Together AI
- `TOGETHER_MODEL_NAME`: AI model name (optional)

## Notes
- The bot will only respond in allowed channels.
- If token space is too low, responses may be limited.

## License
This project is open-source and available under the MIT License.

