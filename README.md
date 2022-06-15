# Dagas
 
Welcome to the repo for the Dagas Project. Some of the things that are needed to work on this project are outlined in this short guide. Read them carefully before attempting to make changes into this repository

## Git guide
Before everything else, you should have <a href="https://git-scm.com/downloads">Git Bash</a> installed on your system. After you have finished installing, you may continue reading on.

### Cloning the repository
Naturally, in order to even begin making changes, you must first have a local copy of the project. This requires cloning the repository to your device, which can be done using the bash command below: 
```bash
git clone https://github.com/EmilJohn24/Dagas.git
```
If you want a more secure connection to the repo, you can set up SSH but I will be discussing this here.

### Experimenting (with branches)
If you want to make significant changes, but are unsure whether it will work out, I would probably recommend you work on a separate branch in your local repository before pushing them here and for that, I will go over this first.

A branch, as the name implies, is a timeline of the project that deviates from the original (the main branch). This means that any changes committed unto the branch will not affect the main branch until they are merged (I will discuss this later). There are two common methods for creating a branch, with slightly different effects:
1. <b>git branch</b>: Creates a branch, but the HEAD stays in the current branch
```bash
git branch <name>
```
2. <b>git checkout</b>: Although
