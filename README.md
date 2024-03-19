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

I compiled the thing for linux (ubuntu) and android, I just need find out how to upload them here

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

