from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from Selenium import scrape_instagram_followers_following

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, you can allow all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InstaCredentials(BaseModel):
    username: str
    password: str

@app.post("/scrape")
async def scrape_instagram(creds: InstaCredentials):
    try:

        follower_following_data = scrape_instagram_followers_following(creds.username, creds.password)
        followers = follower_following_data.get('followers')
        following = follower_following_data.get('following')

        not_following_you_back = list(set(following) - set(followers))
        not_following_them_back = list(set(followers) - set(following))

        return {
            "followers": followers,
            "following": following,
            "not_following_you_back": not_following_you_back,
            "not_following_them_back": not_following_them_back
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    uvicorn.run(app, host="localhost", port=8000)