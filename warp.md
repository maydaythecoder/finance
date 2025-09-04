# Warp Terminal

Warp is a modern, AI-powered terminal built for developers. It combines the power of traditional command-line interfaces with modern UI/UX and AI assistance.

## Key Features

### AI Integration
- **AI Command Search**: Find commands using natural language
- **AI Completions**: Get intelligent autocomplete suggestions
- **AI Error Explanations**: Understand what went wrong with failed commands
- **AI Agent Mode**: Get help with complex development tasks

### Modern Terminal Experience
- **Blocks**: Command output is organized into collapsible blocks
- **Text Selection**: Easy text selection and copying, similar to a text editor
- **Search**: Powerful search through terminal history and output
- **Themes**: Beautiful, customizable themes and color schemes

### Developer Productivity
- **Workflows**: Save and share common command sequences
- **Teams**: Collaborate with team members on terminal sessions
- **Custom Prompts**: Personalize your command prompt
- **Git Integration**: Enhanced git status and branch information

## Installation

### macOS
```bash
brew install --cask warp
```

Or download directly from [warp.dev](https://www.warp.dev)

### Linux
Download the AppImage or .deb package from the official website.

## Getting Started

1. **Sign up**: Create a Warp account for AI features and sync
2. **Import Settings**: Migrate your existing terminal configuration
3. **Explore AI Features**: Try natural language command search
4. **Customize**: Set up themes and preferences

## AI Features

### Command Palette
- Press `Cmd+P` (macOS) or `Ctrl+P` (Linux) to open
- Type natural language descriptions to find commands
- Example: "show disk usage" → suggests `df -h` or `du -sh`

### AI Assistant
- Access through the sidebar or `Cmd+Shift+A`
- Ask questions about commands, errors, or development tasks
- Get explanations and suggestions

### Error Help
- Automatic detection of command failures
- AI-powered explanations and suggested fixes
- Learn from mistakes with contextual help

## Workflows

Create reusable command sequences:

```yaml
name: "Deploy to Production"
steps:
  - git pull origin main
  - npm run build
  - npm run test
  - docker build -t app:latest .
  - kubectl apply -f deployment.yaml
```

## Customization

### Themes
- Built-in themes: Dark, Light, Dracula, etc.
- Custom theme creation
- Import themes from VS Code

### Prompts
- Customize shell prompt appearance
- Add git status, timestamps, or custom information
- Use built-in prompt templates

## Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+P` | Command palette |
| `Cmd+Shift+A` | AI assistant |
| `Cmd+D` | Split pane |
| `Cmd+W` | Close current block |
| `Cmd+K` | Clear terminal |
| `Cmd+T` | New tab |

## Configuration

Warp settings are stored in:
- macOS: `~/.warp/`
- Linux: `~/.config/warp/`

### Key Configuration Files
- `settings.json`: General preferences
- `keybindings.json`: Custom keyboard shortcuts
- `themes/`: Custom theme files
- `workflows/`: Saved workflow definitions

## Teams and Collaboration

- Share workflows with team members
- Sync settings across devices
- Collaborate on debugging sessions
- Share terminal sessions (coming soon)

## Tips and Tricks

1. **Block Navigation**: Use `Cmd+↑/↓` to navigate between command blocks
2. **Quick Search**: `Cmd+R` to search through command history
3. **Copy Mode**: Click and drag to select text like in a text editor
4. **Multiple Cursors**: Hold `Cmd` and click to place multiple cursors
5. **Workflow Shortcuts**: Assign keyboard shortcuts to frequently used workflows

## Troubleshooting

### Common Issues
- **AI features not working**: Check internet connection and Warp account
- **Slow performance**: Clear terminal history or restart Warp
- **Theme issues**: Reset to default theme and reconfigure
- **Shell compatibility**: Ensure your shell (zsh, bash, fish) is supported

### Getting Help
- Documentation: [docs.warp.dev](https://docs.warp.dev)
- Community: [Discord server](https://discord.gg/warp)
- GitHub: [warpdotdev/warp](https://github.com/warpdotdev/warp)

## Advanced Usage

### Custom Scripts Integration
```bash
# Add to your shell profile
export WARP_HONOR_PS1=1  # Use existing prompt
alias wp="warp-cli"      # Warp CLI shortcuts
```

### API Integration
Warp provides APIs for:
- Custom AI completions
- Workflow automation
- Theme development
- Plugin creation

## Resources

- [Official Website](https://www.warp.dev)
- [Documentation](https://docs.warp.dev)
- [Blog](https://blog.warp.dev)
- [Community Discord](https://discord.gg/warp)
- [GitHub Repository](https://github.com/warpdotdev/warp)

---

*Last updated: September 2024*
