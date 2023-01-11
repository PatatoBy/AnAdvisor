## This folder contains the small app written in Python to run the program by the user

In order to work, you need to have an account with [anilist.co](https://anilist.co/)

The app use the available API to retreive your list and use the model developed in this project to recommend you 10 animes

Also be sure to have the followin modules installed:
  - tk
  - joblib
  - requests
  - pandas
  - numpy
  - scikit-learn

#### Unfortunately, the app uses the dataset [`ratings.csv`](https://mega.nz/file/pU9UXQSK#Cr9Vt09zd3vZRleRhsCp6O9OwTWZCh9Jq5KojgSEWeQ) which is 800MB in size, in order to retreive similiar users' list
 - As you download it, it has to be placed in `/source` folder
 - Also remember to adjust file path in the codebase
