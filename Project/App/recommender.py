FILE_PATH_ROOT = 'Project/App'
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
# /\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
import tkinter as tk
from tkinter import ttk
from joblib import load
import requests
import threading

import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

# -----------------------------------------------------------
def loadTask():
  global ratings
  ratings = pd.read_csv(FILE_PATH_ROOT + '/source/ratings.csv').drop(columns = 'Unnamed: 0')
# -----------------------------------------------------------
def scale(table):
  """Scale the given table using StandardScaler
    on the rows
  """
  return pd.DataFrame(
      StandardScaler().fit_transform(table.T),
      index = table.columns, columns = table.index).T
# -----------------------------------------------------------
def recommend(id):
  query = '''
  query ($id: Int) {
    MediaListCollection(userId: $id, type: ANIME) {
      lists {
        entries{
          media {
            idMal
          }
          score
        }
      }
    }
  }
  '''
  variables = {
      'id': id
  }

  url = 'https://graphql.anilist.co'

  response = requests.post(url, json={'query': query, 'variables': variables})

  if response.status_code != 200:
    warningLabel.config(text = f"Error occurred: {response.json()}")
  else:
    edit = response.json()

    myRatings = pd.DataFrame(columns = ['user_id', 'anime_id', 'rating'])
  for LIST in edit['data']['MediaListCollection']['lists']:
    for ITEM in LIST['entries']:
      idMal = ITEM['media']['idMal']
      score = ITEM['score']
      myRatings = myRatings.append({'user_id': 0, 'anime_id': idMal,'rating': score}, ignore_index = True)

  myRatings = myRatings[myRatings.anime_id.isin(anime.index)]
  myRatings['user_id'] = myRatings['user_id'].astype(int)
  myRatings['anime_id'] = myRatings['anime_id'].astype(int)
  myList = myRatings.anime_id.tolist()
  myRatings = myRatings[myRatings['rating'] > 0]

  thread1.join()
  ratingsSupp = ratings
  ratingsSupp = ratingsSupp.append(myRatings)
  # UserID
  x = 0

  # Build the genre profile for the user
  temp = myRatings.join(animeReduced, on = 'anime_id').drop(columns = ['anime_id'])
  temp[genres] = temp[genres].T.multiply(temp['rating']).T
  temp[genres] = temp[genres].replace(0, np.nan)
  temp = temp.drop(columns = 'rating').groupby(by = 'user_id').mean().replace(np.nan,0)
  if temp.shape[0] == 0:
    for row in tableFrame.get_children():
      tableFrame.delete(row)
    for i in range(10):
      tableFrame.insert('','end',values = ('','',''))
    warningLabel.config(text = "Your list is empty, i don't know what to recommend :(")
    return

  # Also scale the user rating list
  scaledTest = scale(temp)
  # Cluster label for tested testUser
  label = kmeans.predict(scaledTest)

  # USers in same cluster
  nearestUsers = clusters[clusters.cluster == label[0]].index
  hiddenList = []
  # Hide things i already seen/not really interested

  nearestUsers = clusters[clusters['cluster'] == label[0]].user_id
  usersList = ratings.loc[ratings.user_id.isin(nearestUsers)].drop(columns = 'user_id')
  usersList['count'] = 1
  meanList = usersList.groupby(by = 'anime_id').sum()
  meanList['rating'] = meanList['rating'] / meanList['count']
  finalList = meanList.join(anime[['name', 'members']])
  topTen = finalList[['name', 'count', 'rating', 'members']].sort_values(by = ['count', 'rating', 'members'], ascending = False)
  mask = (~(ratingsSupp.anime_id.isin(myList)) & ~(ratingsSupp.anime_id.isin(hiddenList)) & (ratingsSupp.user_id.isin(nearestUsers)))
  result = topTen[topTen.index.isin(ratingsSupp.loc[mask].anime_id)].head(10).set_index('name')
  
  for row in tableFrame.get_children():
      tableFrame.delete(row)
  
  if topTen.shape[0] == 0:
    for i in range(10):
      tableFrame.insert('','end',values = ('','',''))
    warningLabel.config(text = "There is nothing for you there...")
  else:   
    for i, row in result.iterrows():
      tableFrame.insert("", "end", text = str(i), values=(int(row['count']), round(row['rating'], 2), int(row['members'])))
# -----------------------------------------------------------
def esegui():
  warningLabel.config(text = '')
  nick = entryBox.get()

  query = '''
  query ($nickname: String) {
      User (name: $nickname) {
          id
      }
  }
  '''
  variables = {
      'nickname': nick
  }

  url = 'https://graphql.anilist.co'

  response = requests.post(url, json={'query': query, 'variables': variables})

  if response.status_code == 404:
    nameLabel.config(text = "User not found")
  elif response.status_code != 200:
    nameLabel.config(text = f"Error occurred: {response.status_code}")
  else:
    userID = response.json()['data']['User']['id']
    nameLabel.config(text = f"{entryBox.get()} ({userID})")
    recommend(userID)
# -----------------------------------------------------------
def del_text(e):
  entryBox.delete(0,'end')
thread1 = threading.Thread(target = loadTask)
thread1.start()
# -----------------------------------------------------------

# print(os.getcwd())
ratings = None
anime = pd.read_csv(FILE_PATH_ROOT + '/source/anime.csv', index_col='anime_id')
clusters = pd.read_csv(FILE_PATH_ROOT + '/source/clusters.csv')
genres = anime.drop(columns = ['episodes', 'type','name','score','popularity','members','favorites']).columns.to_numpy()
animeReduced = anime.drop(columns = ['name','score','type','episodes','members','favorites','popularity'])
kmeans = load(FILE_PATH_ROOT + '/source/model.joblib')

# ---- WINDOW ----
window = tk.Tk()
window.title('AnAdvisor')
window.geometry('550x400+200+200')
window.resizable(False, False)
window.configure(bg = '#363636')
# ---- TEXTBOX ----
entryBox = tk.Entry(width = 20, bg = '#6e6e6e', fg = '#000000', justify= 'center')
entryBox.insert(0, 'Type your nick here')
entryBox.bind('<ButtonPress>', del_text)
entryBox.pack(pady = 20)
# ---- RESPONSE ----
nameLabel = tk.Label(width = 25, bg = '#363636', fg = '#c4c4c4', justify='center')
nameLabel.pack(pady = 5)
# ---- BUTTON ----
performButton = tk.Button(text = 'Recommend me something', bg = '#1d3c91', fg = '#ffffff',
                command = esegui, width = 25)
performButton.pack(pady = 5)
# ---- QUERY RESPONSE ----
warningLabel = tk.Label(width = 450, bg = '#363636', fg = '#c4c4c4', justify='center', font = ('Helvetica', 15))
warningLabel.pack()
# ---- TABLE ----
tableFrame = ttk.Treeview(window, columns=('count', 'rating', 'members'))

style = ttk.Style()
style.theme_use('classic')
style.configure("mystyle.Treeview", background="#363636", fieldbackground="#ffffff", foreground="#c4c4c4")
style.configure("mystyle.Treeview.Heading", background="#1d3c91", foreground="#ffffff")

tableFrame.heading('#0', text = 'Anime name')
tableFrame.heading('count', text = 'Members')
tableFrame.heading('rating', text = 'Avarage vote')
tableFrame.heading('members', text = 'Popularity')

tableFrame.column('#0', width = 200, anchor = 'center')
tableFrame.column('count', width = 5, anchor = 'center')
tableFrame.column('rating', width = 5, anchor = 'center')
tableFrame.column('members', width = 15, anchor = 'center')

tableFrame.configure(style = 'mystyle.Treeview')

tableFrame.pack(side = 'top', fill = 'both', expand = True)

for i in range(10):
  tableFrame.insert('','end',values = ('','',''))
# -------------------
window.mainloop()