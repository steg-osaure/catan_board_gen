Project structure:
    core: `CBGenApp` class, the `toga.App`, instanciate the gui, and game logic, put everything into a single window
    logic: everything related to the board generation. Everything here should operate in board coordinates
    gui: handle the widgets and the drawing. Everything here should be in screen coordinates