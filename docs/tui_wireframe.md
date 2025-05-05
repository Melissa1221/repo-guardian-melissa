# Repo-Guardian TUI Wireframe Design

## Layout Overview

```
+----------------------------------------------------------------------+
|                          REPO-GUARDIAN v0.1.0                         |
+----------------------------------------------------------------------+
|                                                                      |
|  [================ Scanning Repository =================]  75%       |
|                                                                      |
+----------------------------------------------------------------------+
|                                                                      |
|  ERRORS (2)                                | COMMANDS                |
|  ------------------------------------------|--------------------------|
|  [ERROR] Invalid checksum in object        | [R] Repair All          |
|  d8e8fca2dc0f896fd7cb4cb0031ba249         | [F] Fix Selected         |
|  Type: commit                              | [E] Export Graph         |
|                                            | [S] Show Stats           |
|  [WARNING] Potential rewritten history     | [D] Detailed View        |
|  between 8af5cb2 and d95679c              | [Q] Quit                 |
|  Similarity: 0.92                          |                          |
|                                            |                          |
|                                            |                          |
|                                            |                          |
+----------------------------------------------------------------------+
|  STATUS: 2 issues found (1 critical, 1 warning)       [ESC] to exit  |
+----------------------------------------------------------------------+
```

## Components

### Header
- Application title and version
- Progress bar showing current operation status
- Percentage complete indicator

### Main Content Area
Split into two panels:

#### Error Panel (Left)
- Scrollable list of errors and warnings
- Each entry shows:
  - Error type and description
  - Affected object ID (shortened if needed)
  - Additional metadata (object type, similarity score, etc.)
- Color-coded by severity (red for errors, yellow for warnings)

#### Command Panel (Right)
- List of available commands with hotkey shortcuts
- Commands change contextually based on current state
- Highlighted when active/available

### Footer
- Status summary (issues count by severity)
- Keyboard navigation hint

## User Interaction Flow

1. **Start Screen**
   - Initial repository selection or path input
   - Scan button to begin process

2. **Scanning Phase**
   - Progress bar updates in real-time
   - Early issues appear in errors panel as they're found

3. **Results Phase**
   - Full error list displayed
   - Command panel updated with available actions

4. **Repair Phase**
   - User can select individual issues or repair all
   - Progress bar shows repair operation status
   - Success/failure feedback in status bar

## Keyboard Shortcuts

| Key       | Action                           |
|-----------|----------------------------------|
| R         | Repair all issues                |
| F         | Fix currently selected issue     |
| E         | Export repository graph          |
| S         | Show repository statistics       |
| D         | Toggle detailed view for issues  |
| Arrow keys| Navigate issues list             |
| Tab       | Switch between panels            |
| ESC       | Exit or go back                  |
| Q         | Quit application                 |
```
