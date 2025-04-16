from flask import Flask, render_template, request
import pickle
import requests
import os

app = Flask(__name__)

# Load data only once
movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity = pickle.load(open("similarity_list.pkl", 'rb'))
movies_list = movies['title'].values

# Ensure posters folder exists
if not os.path.exists("static/posters"):
    os.makedirs("static/posters")

# Function to download a single poster
def download_poster(movie_title, movie_id):
    file_path = f"static/posters/{movie_id}.jpg"
    if not os.path.exists(file_path):
        url = f"http://www.omdbapi.com/?t={movie_title}&apikey=25a7a02b"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            poster_url = data.get('Poster')
            if poster_url and poster_url != 'N/A':
                try:
                    image_data = requests.get(poster_url).content
                    with open(file_path, "wb") as file:
                        file.write(image_data)
                    return file_path
                except:
                    pass
    return file_path if os.path.exists(file_path) else "https://via.placeholder.com/500x750?text=No+Image"

# Recommendation function
def recommend(movie):
    # Case-insensitive partial match
    filtered = movies[movies['title'].str.contains(movie, case=False, na=False)]
    
    if filtered.empty:
        return []

    index = filtered.index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended = []
    for i in distances[1:6]:
        movie_title = movies.iloc[i[0]].title
        movie_id = movies.iloc[i[0]].id
        poster = download_poster(movie_title, movie_id)
        recommended.append((movie_title, poster))
    return recommended


# Flask route
@app.route("/", methods=["GET", "POST"])
def index():
    recommendations = []
    if request.method == "POST":
        selected_movie = request.form["movie"]
        recommendations = recommend(selected_movie)
    return render_template("index2.html", movies=movies_list, recommendations=recommendations)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

