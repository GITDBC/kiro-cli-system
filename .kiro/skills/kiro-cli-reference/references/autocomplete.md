> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Completions & autocomplete

> AI-powered command completions and suggestions for hundreds of popular CLI tools

Kiro CLI provides two AI-powered assistance features to help you work more efficiently in your terminal:

- **Autocomplete Dropdown Menu**: A graphical menu showing available command options
- **Inline Suggestions**: Gray "ghost text" that appears as you type

These features work independently and support hundreds of popular command line tools including `git`, `npm`, `docker`, and `aws`.

## Autocomplete dropdown menu

The autocomplete dropdown appears to the right of your cursor when typing commands, showing available options, subcommands, and arguments that you can select using arrow keys.

### Using autocomplete

The autocomplete dropdown is automatically enabled after you install Kiro CLI:

1. Open your terminal or command prompt
2. Start typing a command
3. A graphical menu will appear showing available options
4. Use arrow keys to navigate suggestions
5. Press **Tab** or **Enter** to select an option

### Configuration

Customize the autocomplete behavior:

```bash
# Enable/disable autocomplete
kiro-cli settings autocomplete.disable false  # enable
kiro-cli settings autocomplete.disable true   # disable

# Change theme
kiro-cli theme dark
kiro-cli theme light  
kiro-cli theme system

# View current theme
kiro-cli theme

# List available themes
kiro-cli theme --list
```

## Inline suggestions

Inline suggestions appear as gray "ghost text" directly on your command line as you type. This feature works independently from the dropdown menu.

### Using inline suggestions

Inline suggestions are enabled by default:

1. Start typing a command
2. Gray ghost text will appear showing potential completions
3. Press the **right arrow key** or **Tab** to accept
4. Continue typing to ignore the suggestion

### Managing inline suggestions

Control inline suggestions with the `kiro-cli inline` command:

```bash
# Enable inline suggestions
kiro-cli inline enable

# Disable inline suggestions  
kiro-cli inline disable

# Check current status
kiro-cli inline status

# Set customization
kiro-cli inline set-customization [ARN]

# Show available customizations
kiro-cli inline show-customizations
```

## Supported tools

The autocomplete system supports hundreds of command line tools:

### Popular tools
- **Git**: Branch names, commit hashes, file paths
- **Docker**: Container names, image tags, commands
- **npm/yarn**: Package names, scripts, dependencies
- **kubectl**: Resources, namespaces, contexts
- **terraform**: Resources, providers, variables
- **aws**: Services, regions, resource names

### Language tools
- **Python**: `pip`, `poetry`, `conda`
- **Node.js**: `npm`, `yarn`, `pnpm`
- **Ruby**: `gem`, `bundle`
- **Go**: `go mod`, `go build`

### System tools
- Standard Unix/Linux commands
- Package managers (`apt`, `brew`, `yum`)
- File operations (`ls`, `find`, `grep`)

## Troubleshooting

### Autocomplete not working

If autocomplete isn't appearing:

1. Verify installation: `kiro-cli --version`
2. Check if disabled: `kiro-cli settings autocomplete.disable`
3. Restart your terminal
4. Try a different shell (bash, zsh, fish)

### Inline suggestions issues

If inline suggestions aren't working:

1. Check status: `kiro-cli inline status`
2. Enable if disabled: `kiro-cli inline enable`
3. Verify shell compatibility
4. Check terminal emulator support
