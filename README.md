# Dagas
[![Heroku](https://heroku-badge.herokuapp.com/?app=dagas&root=relief/api/users)]
Welcome to the repo for the Dagas Project. Some of the things that are needed to work on this project are outlined in this short guide. Read them carefully before attempting to make changes into this repository
## Special thanks
The development of Dagas required the use of many open-source libraries, all of which are listed in the following files:
* [DagasServer/requirements.txt](./DagasServer/requirements.txt)
* [dagas-react/package.json] (./dagas-react/package.json)
* [build.gradle] (./app/build.gradle)

Finally, we would especially like to thank [Creative Tim Official](https://github.com/creativetimofficial) for the [React Material Dashboard](https://github.com/creativetimofficial/material-dashboard-react), which provides ready-to-use React UI components for the development of our web user interface and the routing system of our React client. Proper acknowledgements can be found in the React code.

## Git guide
Before everything else, you should have <a href="https://git-scm.com/downloads">Git Bash</a> installed on your system. After you have finished installing, you may continue reading on.

### Cloning the repository
Naturally, in order to even begin making changes, you must first have a local copy of the project. This requires cloning the repository to your device, which can be done using the bash command below: 
```bash
git clone https://github.com/EmilJohn24/Dagas.git
```
If you want a more secure connection to the repo, you can set up SSH but I will not be discussing this here.

### Experimenting (with branches)
If you want to make significant changes, but are unsure whether it will work out, I would probably recommend you work on a separate branch in your local repository before pushing them here and for that, I will go over this first.

A branch, as the name implies, is a timeline of the project that deviates from the original (the main branch). This means that any changes committed unto the branch will not affect the main branch until they are merged (I will discuss this later). There are two common methods for creating a branch, with slightly different effects:
1. <b>git branch</b>: Creates a branch, but the HEAD stays in the current branch
```bash
git branch <name>
```
2. <b>git checkout</b>: Can be used to create a branch, but the HEAD moves to the new branch
```bash
git checkout -b <name>
```
- <b>Note</b>: The ```bash git checkout``` is actually used to transfer to a different branch but the -b flag is used so that the branch is created if it does not exist.

To get a complete list of all the branches in the project, you can use:
```bash
git branch
```
To transfer between branches, you can use
```bash
git checkout <name>
```

### Components
This project has three primary components:
1. <b>[DagasServer](./DagasServer/)</b>: This contains the backend server code for Dagas written in Python Django and DRF.
2. <b>[DagasAndroid](./DagasAndroid/)</b>: This contains the code for the Android client
3. <b>[dagas-react](./dagas-react/)</b>: This contains the code for the Dagas React server, which will serve HTML content to the user