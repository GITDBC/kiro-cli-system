> ## Documentation Index
> Fetch the complete documentation index at: https://kiro.dev/llms.txt
> Use this file to discover all available pages before exploring further.

# Working with Git

> When working with Git repositories, Kiro CLI's fuzzy finder is Git-aware, making it easier to select and add relevant files to your context. This feature helps you quickly identify and include files that are part of your Git repository.

When working with Git repositories, Kiro CLI's fuzzy finder is Git-aware, making it easier to select and add relevant files to your context. This feature helps you quickly identify and include files that are part of your Git repository.

## How Git-aware selection works

The Git-aware fuzzy finder automatically integrates with your repository's Git information to provide enhanced file selection capabilities:

* Recognizes Git-tracked files in your repository
* Shows Git status indicators alongside files
* Prioritizes relevant files based on Git history

## Using Git-aware file selection

###### To use git-aware file selection

1. Navigate to your Git repository in the terminal.
2. Run the context add command:

   ```
   /context add
   ```
3. In the fuzzy finder interface, you'll see files from your repository with Git status indicators:

   * `M` – Modified files
   * `A` – Added files
   * `?` – Untracked files
4. Type to filter files, using Git status as part of your search criteria.
5. Use the arrow keys to navigate and press Enter to select files to add to your context.

## Tips for Git-aware selection

* Use Git status indicators in your search to quickly find modified or untracked files
* The fuzzy finder prioritizes recently modified files in Git history
* Files ignored by Git (via .gitignore) are still available but deprioritized in the results
