# Catan Board Generator
Generate random, balanced boards for the board game Catan

This program lets you generate random boards for the board game of Catan.
Several options are available to make the board more balanced, for instance,
prevent to many tiles of the same ressource type to be neighbouring each other.
An option to generate bigger boards for the 5th and 6th player extension is also 
available.

## Getting started

This program is made using [Briefcase](https://briefcase.readthedocs.io/),
part of the [BeeWare Project](https://beeware.org/), in order to make it cross-platform.

### Pre-built binaries

You can find linux (ubuntu) binaries and android apk in the [Release](https://github.com/steg-osaure/catan_board_gen/releases) page.

I do not have a Windows PC or a Mac, so I don't have a way to compile binaries for 
Windows, Mac and iOS, so refeer to the following section to build from source.

### Building it from source

You will need to install beeware and briefcase, instructions can be found on 
[this tutorial](https://docs.beeware.org/en/latest/tutorial/tutorial-0.html).

After having installed and activated a `beeware` environment, do the following:

```
git clone https://github.com/steg-osaure/catan_board_gen
cd catan_board_gen
briefcase create
briefcase build
briefcase run
```

## Planned updates:

This is the roadmap for future updates:

   - 0.0.3: round up base game implementation
      - [X] Implement random port placement (with big border tiles)
      - [ ] Add smaller board (3 player) variant

   - 0.1.0: Making code cleaner:
      - [X] Refactor code such that:
         - [X] one class handles the UI and display 
         - [X] one class handles the board logic
         - [X] one class for the individual tiles (already the case)
      - [X] Fix remaining temporary solutions and TODOs

   - 0.2.0: Seafarers boards
      - [ ] Add option to use seafarer boards, implement board layouts from scenarios that do not require exploration
      - [ ] UI redesign to deal with added options from seafarer

   - 0.2.1: Seafarers exploration mode
      - [ ] Add "exploration mode", where the board is generated, but tiles can be revealed one at the time, like in some seafarer scenarios
      - [ ] Add remaining seafarers board layouts
