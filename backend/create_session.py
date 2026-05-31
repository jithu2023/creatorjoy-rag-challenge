import instaloader

USERNAME = input("Enter your Instagram username: ")

L = instaloader.Instaloader()

# Try to load existing session
try:
    L.load_session_from_file(USERNAME)
    print(f"✅ Session loaded for {USERNAME}")
except FileNotFoundError:
    print(f"No session found. Logging in for {USERNAME}...")
    password = input(f"Enter password for {USERNAME}: ")
    L.login(USERNAME, password)
    L.save_session_to_file()
    print(f"✅ Session saved for {USERNAME}")

# Verify login worked
print(f"Logged in as: {L.test_login()}")
print(f"User ID: {L.context.user_id}")