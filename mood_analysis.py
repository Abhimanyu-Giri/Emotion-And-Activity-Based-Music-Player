from textblob import TextBlob

def get_mood(text):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0.2:
        return "positive"
    elif polarity < -0.2:
        return "negative"
    else:
        return "neutral"

def is_gym_related(text):
    keywords = [
        "gym", "workout", "exercise", "lifting", "training", "fitness", 
        "cardio", "leg day", "chest day", "arms", "deadlift", "squats", 
        "bench press", "treadmill", "dumbbell", "barbell", "stretching",
        "strength", "HIIT", "calisthenics", "crossfit"
    ]
    text = text.lower()
    return any(word in text for word in keywords)
