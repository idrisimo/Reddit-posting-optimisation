''' This program will indicate the best time to post, based on the top 500 posts of all time.'''
import praw
from prawcore import NotFound, ResponseException
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize
from matplotlib import cm
from scipy.stats import gaussian_kde as kde

# TODO sort out authentication so that my account doesnt have to be used.
def reddit_auth(): # connects to reddit
    client_id = input("Enter client id:")
    client_secret = input("Enter client secret:")
    dev_app_name = input("Enter your reddit dev app name:")
    user_agent = input("Enter user name without the 'u/':")
    reddit = praw.Reddit(client_id=f"{client_id}",
                         client_secret=f"{client_secret}",
                         user_agent= f"{dev_app_name} by u/{user_agent}")
    return reddit



def reddit_data(reddit_auth, subreddit_name):
    subData = {}

    subreddit = reddit_auth.subreddit(subreddit_name)
    # Collects top 500 posts of all time on chosen subreddit.
    # Then grabs the day of week and the time the post was made which is stuck into an array to be used by matplot.
    for submission in subreddit.top('all', limit=500):
        time_created = datetime.fromtimestamp(submission.created_utc)
        day_of_week = time_created.weekday()
        time_of_day = time_created.time()
        time_of_day_seconds = timedelta(hours=time_of_day.hour, minutes=time_of_day.minute, seconds=time_of_day.second).total_seconds()
        subData.setdefault(submission.id, {"Day of week": day_of_week, "Time of day": int(time_of_day_seconds)})
    subFrame = pd.DataFrame(subData).T
    return subFrame.sort_values(by="Time of day")

def display_heatmap(data):
    X = data['Day of week']
    Y = data['Time of day']
    # Creates a 3rd variable for the density of the dots.
    samples = [X, Y]
    densObj = kde(samples)

    # Converts dots into a red/blue heatmap. Not entirely sure how. See link:
    # https://stackoverflow.com/questions/19064772/visualization-of-scatter-plots-with-overlapping-points-in-matplotlib
    def makeColours(vals):
        colours = np.zeros((len(vals), 3))
        norm = Normalize(vmin=vals.min(), vmax=vals.max())
        colours = [cm.ScalarMappable(norm=norm, cmap="jet").to_rgba(val) for val in vals]
        return colours
    colours = makeColours(densObj.evaluate(samples))

    # Labels for the X and Y tickers
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    time = ["Midnight", "1am", "2am", "3am", "4am", "5am", "6am", "7am", "8am", "9am", "10am", "11am", "12pm",
            "1pm", "2pm", "3pm", "4pm", "5pm", "6pm", "7pm", "8pm", "9pm", "10pm", "11pm"]
    # Place Labels in the right spot by only allowing a certain amout of ticks
    plt.xticks(np.arange(7), labels=day_order)
    # Same as above but done by taking lowest value, highest value, and the steps between.
    # Essentially divide 86000 by 24 to get steps.
    plt.yticks(np.arange(0, 86400, 3600), labels=time)

    # Creates graph.
    plt.scatter(samples[0], samples[1], color=colours, s=1000, marker='s')
    plt.margins(y=0.01)
    #plt.tight_layout()
    plt.show()


def start_script():
    print("------------Welcome to 'When-to-post' for Reddit!------------")
    print("This program will indicate the best time to post for your chosen subreddit,"
          "based on the top 500 posts of all time.")
    try:
        auth = reddit_auth()


        run_script = True
        while run_script == True:
            subreddit_name = input("Please select your chosen subreddit (without 'r/'):")
            sub_exists = False
            while sub_exists == False:
                try:
                    auth.subreddits.search_by_name(subreddit_name, exact=True)
                    sub_exists = True
                except NotFound:
                    print(f"'{subreddit_name}' does not exist. Please try again")
                    subreddit_name = input("Please select your chosen subreddit (without 'r/'):")



            data = reddit_data(auth, subreddit_name)

            display_heatmap(data)
            quit_script = input("Want to quit? Y/N:")
            if quit_script.upper() == "Y":
                print("Have a good day!")
                run_script = False
            else:
                continue
    except ResponseException:
        print(
            "Authentication details incorrect please see https://github.com/reddit-archive/reddit/wiki/OAuth2 "
            "to ensure you have the right authentication details")
start_script()