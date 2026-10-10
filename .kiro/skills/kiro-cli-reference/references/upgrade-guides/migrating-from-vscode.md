> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Migrating from VSCode

> Comprehensive guide for transitioning from Visual Studio Code to Kiro's AI-powered development environment

Built on Visual Studio Code's open source foundation, Kiro delivers AI-enhanced development capabilities while preserving the familiar interface you know. This shared architecture ensures a smooth transition when bringing your existing VS Code configuration to Kiro.

## Profile migration

Kiro's VS Code foundation enables complete compatibility with your development environment. You can transfer your personalized setup—extensions, themes, configurations, and shortcuts—with no compatibility concerns.

### Manual profile migration

For cross-machine transfers or granular control over your configuration, leverage VS Code's native profile export/import capabilities.

#### Exporting a profile from vs code

1. Launch the **Command Palette** in VS Code (`⌘`/`Ctrl` + `Shift` + `P`).
2. In the **Command Palette**, enter and select "Preferences: Open Profiles (UI)".
3. Locate your desired profile in the sidebar.
4. Access the 3-dot menu and choose **Export**.
5. Save locally or publish to a GitHub Gist.

![VS Code profile export interface showing the export options](https://kiro.dev/images/vscode-migrate-1-export-profile.png)

#### Importing a profile to Kiro

1. Access Kiro's **Command Palette** (`⌘`/`Ctrl` + `Shift` + `P`).
2. In the **Command Palette**, enter and select "Preferences: Open Profiles (UI)".
3. Open the dropdown beside **New Profile** and select **Import Profile**.
4. Provide the GitHub Gist URL or browse for your local export file.
5. Confirm by choosing **Import** to save your configuration.
6. Activate your profile by selecting it in the sidebar and selecting the checkmark.

Your imported profile includes:
- Color themes and UI preferences
- Editor and workspace settings
- Custom keyboard shortcuts and keybindings

## Settings and interface

### Settings menus

Kiro extends VS Code's settings architecture with dedicated controls for AI capabilities:

**Kiro Settings**
- Open Settings: **Command Palette** (`⌘`/`Ctrl` + `Shift` + `P`) → "Preferences: Open Settings (UI)"
- Navigate to **Kiro Agent** section within the settings UI
- Manage AI behaviors, agent automation, trusted commands, and Kiro-exclusive features

![Kiro Agent settings within the VS Code settings UI](https://kiro.dev/images/vscode-migrate-5-kiro-settings.png)

**VS Code Settings**
- Access the same way: **Command Palette** (`⌘`/`Ctrl` + `Shift` + `P`) → "Preferences: Open Settings (UI)"
- Your standard VS Code preferences remain fully functional alongside Kiro settings

### Version updates

Kiro stays synchronized with VS Code's development cycle through regular rebasing. While we incorporate the latest features and improvements, we strategically select stable VS Code releases to ensure reliability alongside our AI enhancements.

## Extension compatibility

Kiro uses the OpenVSX extension registry, ensuring compatibility with open-source extensions. Extensions available in OpenVSX will migrate seamlessly, with many gaining enhanced capabilities through Kiro's AI integration:

- **Language extensions**: Full functionality preserved for OpenVSX-available extensions
- **Theme extensions**: Complete visual compatibility with OpenVSX themes
- **Debugging extensions**: Uninterrupted debugging workflows for compatible extensions
- **Git extensions**: Augmented with intelligent commit generation and automated code review

**ℹ️ Info:** Only extensions available in the OpenVSX registry can be imported. Some VS Code Marketplace exclusives may not be available in Kiro.
