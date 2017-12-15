# SI-364-Final - Samantha Moross: iTunes Music Video API 

# To Run My Application
Create the database smorossFinal by writing the terminal command 'createdb smorossFinal' before running my application. 
Input the terminal command python 'Final.py' runserver in order to run my application. This will connect your server to 
local host 5000. You can input http://localhost:5000 into your browser to reach the application. No additional imports are necessary. 

# What My Application Does
My application is designed for users who are interested in music to search for music videos and create music video playlists.

Once a user logs in or creates an account, my application directs the user to a form (using a WTForm.) The user is promted to search 
for an artist or song title, and receives a resulting list of music video titles along with the artist, genre, and track price 
(assuming the user may be interested in purchasing the track.) Each song title is a hyperlink (dynamic link), and when clicked on,
directs the user to a preview of the music video. The user can play/pause the video, adjust the video sound, make the video full-screen,
and even download the video by clicking the download button on the bottom left of the video. Above the video, the user has the option to
add the video to one of their music video playlists (If the user has no playlists yet, they can navigate to the route '/form' and create
a new playlist name.) Once the user clicks 'Add song to playlist,' the app navigates to the '/playlists' route, which shows a list of 
all the users playlists with the song titles under each one. Above each playlist, there is an option for the user to upload an image 
to compliment the playlist. When the user selects, 'Show Art,' the browser flashes the link that will display this image (using AJAX).
All of these files are saved to the cover_art table in the smorossFinal database.

# Database Tables
In my application, there are 5 database tables: users, playlists, music videos, cover art, and an association table for playlists and music videos. Playlists and music videos have a many to many relationship because a single music video can be added to many playlists, and a single playlist can have many music videos. An association table for music videos and playlists accounts for this, tracking the playlist id and music video id as a user saves a music video to one of their playlists. A one to many relationship example in this database is users to playlists. One user can have many playlists, but one playlist can only be assigned to a single user. 