# README.md

## To start development:
1.  Clone this repository to your computer
2.  Open the cloned folder in VS Code
3.  Open Terminal in VS Code (Terminal > New Terminal)
4.  Switch to the develop branch in Terminal `git checkout develop` (Or switch the branch in the bottom left corner of VS Code)
5.  Create a new conda environment and activate it in your local machine by `conda env create -f env.yml` and `conda activate btcbot`
6.  Setting the VS Code to use the conda environment you just created (**Ctrl + Shift + P > Python: Select Interpreter > btcbot**)
7.  Run the code in **main.ipynb**

   
## Update some packages during development:
1.  If you want to install some new packages, please remember to **manually add them to the env.yml without any version and os dependencies**. Please **DON'T** export it by `conda env export --no-builds > env.yml` because it will causes some ResolvePackageNotFound Error. For example, if you run the command `pip install ipykernel ` then you can add a line at the bottom of the env.yml like `- ipykernel`.
2.  If you want to deactive the conda environment, please use `conda deactivate`
3.  If you want to delete your local conda environment, please use `conda env remove -n btcbot`

## Git commands:
1.  If you want to push your code, please use `git push origin <branch-name>` after using `git add .` and `git commit -m "<your commit message>"` (You need to set the `origin` url first)
2.  If you want to pull the latest code, please use `git pull origin <branch-name>` (You need to set the `origin` url first)
3.  If you want to create a new branch, please use `git checkout -b <branch-name>` (We use the develop branch as the default development branch, and when we finish a version, we will merge the develop branch to the main branch). Then you can push it to the github by `git push origin <branch-name>`.
