# install github locally and setup
in order to access github remotely via git from the local machine, it was not anymore sufficient to use the github username and password (2-factor-auth. disabled!). instead, github had to be installed on the local machine and then a remote connection was established. 

1. create a github account.

2. install github cli on linux: https://github.com/cli/cli/blob/trunk/docs/install_linux.md

3. authenticate remote connection: https://docs.github.com/en/get-started/getting-started-with-git/caching-your-github-credentials-in-git

4. configure git locally:

`git config --global user.email "your.mail@server.de`

`git config --global user.name "your name"`


# download public repository to local machine ("clone")
download repo to pwd:

`git clone https-to-repo`

move to new repo folder:

`cd folder-of-repo`

check repo status:

`git status`


# workflow for creating a new feature branch

update repo to newest state:

`git pull`

open a new branch to work on:

`git branch branch-name`

if not there already, change to the new branch and check if correct:

`git switch branch-name`

`git status`

after some changes were made, add (-a = all) and commit your changes:

`git add -A`

`git commit -m "short comment what changed"`


publish the modifications in the central remote repo (will be reviewed before merging):

`git push`

(or more generally: `git push -u origin branch-name`)

when the branch goal is reached, it can be merged with main in github.
Alternatively, merging with main can be performed locally:

`git switch main`

`git merge`

# Handling pull requests

to test proposed changes locally:
[https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/checking-out-pull-requests-locally](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/checking-out-pull-requests-locally)

git ID of pull request from github webpage

fetch pull request and create new branch:

`git fetch origin pull/ID/head:BRANCH_NAME`

switch to new branch:

`git switch BRANCH_NAME`

or

`git checkout BRANCH_NAME`

now do all necessary tests and modifications; when done, push the branch up:

`git push origin BRANCH_NAME`

create new pull request with the branch and merge 


