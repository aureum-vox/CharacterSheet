# 5.5e Dynamic Character Sheet

## Phase 1: Repository & Folder Structure
- [x] Initialize the Git repository and create a .gitignore file.
- [x] Add the temp/ directory to .gitignore (prevents committing ephemeral working files).
- [x] Add the logs/ directory to .gitignore (keeps run logs local).
- [x] Create the data/ folder for repository pull scripts and JSON parsing logic.
- [x] Create the gui/ folder for UI layouts, widgets, and window management.
- [x] Create a main.py at the root directory to serve as the unified application entry point.

## Phase 2: Data Layer Development
- [ ] Write the script to fetch the 5.5e JSON files from the 5etools GitHub mirror.
- [ ] Implement a caching mechanism to save downloaded JSONs to the temp/ working directory.
- [ ] Build the parsing logic to filter specifically for 2024 ("XPHB") tags.
- [ ] Create a Python Character class to hold stats, features, and level progression in memory.
- [ ] Add standard logging to record successful API pulls, cache reads, and parsing errors to the logs/ folder.

## Phase 3: GUI Layer Development
- [ ] Initialize the main desktop window using your chosen framework.
- [ ] Build the static UI components (ability score boxes, saving throw checkboxes, skill list).
- [ ] Build the dynamic UI components (scrollable feature lists, dynamic spell slots based on level).
- [ ] Create event listeners (e.g., a "Level Up" button click) that will eventually trigger data updates.
- [ ] Test the UI responsiveness using mocked character data.

## Phase 4: Integration & Delivery
- [ ] Import the data layer functions into main.py or your GUI event loop.
- [ ] Bind the GUI event listeners to your Character class so state changes update the UI text visually.
- [ ] Configure the GUI to trigger the data layer's repo pull on first launch if the temp/ cache is empty.
- [ ] Write a build configuration to compile the entire project into a single .exe file for Windows.
