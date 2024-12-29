###### packages and dependencies ######
import sqlite3

import numpy as np
import pandas as pd

####################################################################################################
###### USER ######
class User:
    def __init__(self, user_id, name, password, MBTI, age, gender, location, interests,
                 liked_users=None, disliked_users=None, matches=None):
        self.user_id = user_id
        self.name = name
        self.password = password
        self.MBTI = MBTI
        self.age = age
        self.gender = gender
        self.location = location
        self.interests = interests
        self.liked_users = liked_users if liked_users is not None else []
        self.disliked_users = disliked_users if disliked_users is not None else []
        self.matches = matches if matches is not None else []
        

    def like(self, other_user):
        if other_user.user_id not in self.liked_users:
            self.liked_users.append(other_user.user_id)
        if self.user_id in other_user.liked_users and other_user.user_id not in self.matches:
            self.matches.append(other_user.user_id)
            other_user.matches.append(self.user_id)

    def dislike(self, other_user):
        if other_user.user_id not in self.disliked_users:
            self.disliked_users.append(other_user.user_id)

    # adding data field name for easy reading
    def __repr__(self):
        return (f"User ID: {self.user_id}, Name: {self.name}, MBTI: {self.MBTI}, "
                f"Age: {self.age}, Gender: {self.gender}, Location: {self.location}, "
                f"Interests: {', '.join(self.interests)}")


    ###### Data formatting ######
    def object_to_db(self):
        """Convert the user data to a format suitable for the database."""
        return (
            self.user_id,
            self.name,
            self.password,
            self.MBTI,
            self.age,
            self.gender,
            self.location,
            ','.join(self.interests),
            ','.join(map(str, self.liked_users)),
            ','.join(map(str, self.disliked_users)),
            ','.join(map(str, self.matches))
        )

    @staticmethod
    def db_to_object(data):
        """Create a User object from a database record."""
        user_id, name, password, MBTI, age, gender, location, interests, liked_users, disliked_users, matches = data
        
        return User(
            user_id,
            name,
            password,
            MBTI,
            age,
            gender,
            location,
            interests.split(',') if interests else [],
            list(map(int, liked_users.split(','))) if liked_users else [],
            list(map(int, disliked_users.split(','))) if disliked_users else [],
            list(map(int, matches.split(','))) if matches else []
        )
####################################################################################################


####################################################################################################
###### Database Manipulation ######
def insert_user(user):
    try:
        conn = sqlite3.connect('users.db')    
        cursor = conn.cursor()    
        cursor.execute('''
            INSERT INTO users (name, password, MBTI, age, gender, location, interests, liked_users, disliked_users, matches)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', user.object_to_db()[1:])
    except Exception as e:
        conn.close()
        print('Exception: {}'.format(e))
        raise Exception(e)
    else:
        conn.commit()
        conn.close()

def update_user(user):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE users
            SET name = ?, password = ?, MBTI = ?, age = ?, gender = ?, location = ?, interests = ?, liked_users = ?, disliked_users = ?, matches = ?
            WHERE user_id = ?
        ''', (*user.object_to_db()[1:], user.user_id))
    except Exception as e:
        conn.close()
        print('Exception: {}'.format(e))
        raise Exception(e)
    else:
        conn.commit()
        conn.close() 

def delete_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # First, update other users' liked_users, disliked_users, and matches lists to remove this user
    cursor.execute('SELECT * FROM users')
    all_users = cursor.fetchall()

    for user_data in all_users:
        (current_user_id, name, password, MBTI, age, gender, location, interests, liked_users, disliked_users, matches) = user_data

        liked_users_list = list(map(int, liked_users.split(','))) if liked_users else []
        disliked_users_list = list(map(int, disliked_users.split(','))) if disliked_users else []
        matches_list = list(map(int, matches.split(','))) if matches else []

        if user_id in liked_users_list:
            liked_users_list.remove(user_id)
        if user_id in disliked_users_list:
            disliked_users_list.remove(user_id)
        if user_id in matches_list:
            matches_list.remove(user_id)

        # Update the current user with the modified lists
        liked_users = ','.join(map(str, liked_users_list))
        disliked_users = ','.join(map(str, disliked_users_list))
        matches = ','.join(map(str, matches_list))

        cursor.execute('''
            UPDATE users
            SET liked_users = ?, disliked_users = ?, matches = ?
            WHERE user_id = ?
        ''', (liked_users, disliked_users, matches, current_user_id))

    # Now delete the user from the database
    cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))

    conn.commit()
    conn.close()

    print("User deleted successfully! Logged out!")



def create_user():
    # user_id is auto-generated by the database
    name = input("Enter name: ")
    password = input("Enter password: ")
    
    # Take user input and check database constraints
    MBTI = input("Enter MBTI: ")
    while MBTI not in ("ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"):
        MBTI = input("Please enter a valid MBTI: ") 

    age = input("Enter age: ")
    while True: 
        try:
            age = int(age)
        except:
            age = input("Please enter an integer: ") 
        else:
            break

    gender = input("Enter gender (Female/Male): ")
    while gender not in ("Female", "Male"):
        gender = input("Please enter a valid gender: ")
    
    location = input('''Enter a city from the following list: 
                     Barrie, Belleville, Brampton, Brantford,
                     Burlington, Cambridge, Greater Sudbury,
                     Guelph, Hamilton, Kitchener, London, Markham,
                     Mississauga, Niagara Falls, Norfolk County,
                     North Bay, Oshawa, Ottawa, Peterborough,
                     Pickering, Richmond Hill, Sarnia,Sault Ste. Marie,
                     St. Catharines, Thunder Bay, Toronto, Vaughan,
                     Waterloo, Welland, Windsor\n''')
    while location not in ("Barrie", "Belleville", "Brampton", "Brantford", 
                           "Burlington", "Cambridge", "Greater Sudbury", "Guelph", 
                           "Hamilton", "Kitchener", "London", "Markham", "Mississauga", 
                           "Niagara Falls", "Norfolk County", "North Bay", "Oshawa", 
                           "Ottawa", "Peterborough", "Pickering", "Richmond Hill", 
                           "Sarnia", "Sault Ste. Marie", "St. Catharines", 
                           "Thunder Bay", "Toronto", "Vaughan", "Waterloo", "Welland", 
                           "Windsor"):
        location = input("Please enter a valid city: ")

    print('''Enter interests one by one. Press enter after each. Enter END blank to stop adding.
          Select from the following list:
          Collecting, Clothing, Cooking, Gardening, Models, 
          Outdoors, Travelling, Fitness, Games, Sports, 
          Dancing, Music, Theater, Visual, Literary''')
    interest = input()
    interests = []
    while interest != "END":
        if interest in ("Collecting", "Clothing", "Cooking", "Gardening", "Models", "Outdoors", 
                        "Travelling", "Fitness", "Games", "Sports", "Dancing", "Music", "Theater", 
                        "Visual", "Literary"):
            interests.append(interest)
            interest = input("Add another interest: ")
        else:
            interest = input("Please enter a valid interest: ")
    
    # Check if the name is unique
    while True:
        newUser = User(-1, name, password, MBTI, age, gender, location, interests)
        try:
            insert_user(newUser)
        except:
            name = input("Name has been registered. Enter a new name: ")
        else:
            break
    print("User created successfully. Please log in.")

###### Database Query ######
def fetch_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    data = cursor.fetchone()
    conn.close()    

    if data:
        user = User.db_to_object(data)
        return user
    else:
        print("No user found with the given user_id.")
        return None

# Display one user profile based on user id
def view_one_profile(user_id):
    profile = fetch_user(user_id)
    print(repr(profile))

# 
def view_all_profiles(user, except_currnet_user=None):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    profiles = cursor.fetchall()
    conn.commit()
    conn.close()
    
    if except_currnet_user:
        for profile in profiles:
            other = User.db_to_object(profile)
            if other.user_id != user.user_id:
                print(repr(other))
    else: 
        for profile in profiles:
            print(repr(other))
####################################################################################################


####################################################################################################
###### Authorization ######
def authenticate(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users where name = ?', (username,))
    profile = cursor.fetchone()
    conn.close()
    
    user = User.db_to_object(profile)

    if user.password == password:
        return user
    else:
        return None

def login():
    username = input("Enter your name: ")
    password = input("Enter your password: ")
    try: 
        user = authenticate(username, password)
    except:
        print("Invalid credentials.")
        return None
    
    if user:
        print("Login successful!")
        return user
    else:
        print("Invalid credentials.")
        return None

    
    
#########################################################################################################


####################################################################################################
###### Matching Algorithm ######

# Load all users except for the current user and the ones he/she (dis)liked
def fetch_valid_users(user):
    exclusion = [user.user_id]
    exclusion.extend(user.disliked_users)
    exclusion.extend(user.liked_users)

    conn = sqlite3.connect('users.db')
    placeholders= ', '.join("?"*len(exclusion))
    query = 'SELECT * FROM users where user_id not in ({0})'.format(placeholders)
    df = pd.read_sql_query(query, conn, params=tuple(exclusion))

    # Convert each comma-separated string in the 'interests' column to a list of interests
    df['interests_list'] = df['interests'].apply(
    lambda x: x.split(',') if x else [])
    conn.commit()
    conn.close()
    return df

#Compute Compatibility Scores and return top 5
def compute_compatibility_scores(current_user, gender_preference):
    potential_matches = fetch_valid_users(current_user).copy()
    if potential_matches.empty:
        print("Sorry! Currently we do not have more potential matches for you.")
        return potential_matches

    # Caculate gender compatibility score using a boolean mask and convert to float
    if gender_preference == "Both":
        potential_matches['gender_score'] = 1.0
    else:
        potential_matches['gender_score'] = (potential_matches['gender'] == gender_preference).astype(float)

    # Calculate location compatibility score using a boolean mask and convert to float
    potential_matches['location_score'] = (potential_matches['location'] == current_user.location).astype(float)

    # Calculate age difference score using NumPy's vectorized operations
    potential_matches['age_diff_score'] = 1 / (1 + np.abs(potential_matches['age'] - current_user.age))

    # retrieve current user's MBTI for following comparison
    mbti1 = current_user.MBTI
    # Caculate gender compatibility score
    def calculate_mbti_scores(mbti2):
        # Compare each letter of MBTI
        # Opposite E/I scores 2; for the rest, same personality scores 1 point
        mbti_score = 0.0
        if mbti1[0] != mbti2[0]:
            mbti_score += 2.0
        if mbti1[1] == mbti2[1]:
            mbti_score += 1.0
        if mbti1[2] == mbti2[2]:
            mbti_score += 1.0
        if mbti1[3] == mbti2[3]:
            mbti_score += 1.0

        return mbti_score / 5.0

    potential_matches['MBTI_score'] = potential_matches['MBTI'].apply(calculate_mbti_scores)
    
    # Convert interests lists into a set for the logged-in user for faster comparison
    current_interests_set = set(current_user.interests)

    # Optimize shared interests score calculation using list comprehension and apply
    def calculate_jaccard_similarity_vectorized(interests):
        # Convert list to set for potential matches
        interests_set = set(interests)
        # Calculate intersection and union sizes directly
        intersection_size = len(current_interests_set & interests_set)
        union_size = len(current_interests_set | interests_set)
        # Return the Jaccard similarity score
        return intersection_size / union_size if union_size > 0 else 0

    # Apply the vectorized Jaccard similarity calculation to all potential matches
    potential_matches['interests_score'] = potential_matches['interests'].apply(calculate_jaccard_similarity_vectorized)

    # Combine the individual scores into a final compatibility score using NumPy's vectorized operations
    potential_matches['compatibility_score'] = (
        0.4 * potential_matches['gender_score'] +
        0.15 * potential_matches['MBTI_score'] +
        0.1 * potential_matches['age_diff_score'] +
        0.2 * potential_matches['location_score'] +
        0.15 * potential_matches['interests_score']
    )

    # Sort by the compatibility score in descending order
    potential_matches = potential_matches.sort_values(by='compatibility_score', ascending=False)

    return potential_matches.head(5)

def mark_user(user, other_user):
    while True:
        print("\nPlease mark the user. Type STOP to quit at any time")
        choice = input("1 for Like \n2 for Dislike\nYour choice: ")
        if choice == '1':
            user.like(other_user)
            update_user(user)
            update_user(other_user)
            break
        elif choice == '2':
            user.dislike(other_user)
            update_user(user)
            update_user(other_user)
            break
        elif choice == "STOP":
            print("Stop matching")
            break
        else:
            print("Invalid choice. Please try again.")

def start_matching(user):
    gender_preference = input("Please specify your preference for this matching (Female/Male/Both): ")
    while gender_preference not in ("Female", "Male", "Both"):
        gender_preference = input("Please enter a valid gender: ")

    potential_matches = compute_compatibility_scores(user, gender_preference)
    size = len(potential_matches)
    if size == 0:
        return None
    
    potential_matches = potential_matches.reset_index(drop=True)    
    for i in range(size):
        other_user_id = potential_matches.loc[i,"user_id"]
        other_user = fetch_user(int(other_user_id))
        print(f"\nSee your Potential Match No.{i+1}")
        print(potential_matches.loc[i, ["name","MBTI", "age", "gender", "location", "interests"]])
        mark_user(user, other_user)    

####################################################################################################


###### Other Utility Functions ######
def update_profile(user):
    print(f"Your name is {user.name}. This cannot be modified.\n")
    
    new_password = input(f"Enter your new password. Leave blank to keep '{user.password}'.\nNew password: ")
    if new_password:
        user.password = new_password
    
    new_MBTI = input(f"Enter your new MBTI. Leave blank to keep '{user.MBTI}'.\nNew MBTI: ")
    if new_MBTI:
        while new_MBTI not in ("ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", 
                           "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"):
            new_MBTI = input("Please enter a valid MBTI: ") 
        
        user.MBTI = new_MBTI
    
    new_age = input(f"Enter your new age (an integer). Leave blank to keep '{user.age}'.\nNew age: ")
    if new_age:
        while True: 
            try:
                user.age = int(new_age)
            except:
                new_age = input("Please enter a valid integer: ") 
            else:
                break

    new_gender = input(f"Enter new gender(Female/Male). Leave blank to keep '{user.gender}'.\nNew Gender: ")
    if new_gender:
        while new_gender not in ("Female", "Male"):
            new_gender = input("Please enter a valid gender: ")
        
        user.gender = new_gender
        
    new_location = input(f"Enter your new location. Leave blank to keep '{user.location}'). "
                        f"\n  Enter a city from the following list: "
                        f"\n  Barrie, Belleville, Brampton, Brantford,"
                        f"\n  Burlington, Cambridge, Greater Sudbury,"
                        f"\n  Guelph, Hamilton, Kitchener, London, Markham,"
                        f"\n  Mississauga, Niagara Falls, Norfolk County,"
                        f"\n  North Bay, Oshawa, Ottawa, Peterborough,"
                        f"\n  Pickering, Richmond Hill, Sarnia,Sault Ste. Marie,"
                        f"\n  St. Catharines, Thunder Bay, Toronto, Vaughan,"
                        f"\n  Waterloo, Welland, Windsor\nNew location: ")
    if new_location:
        while new_location not in ("Barrie", "Belleville", "Brampton", "Brantford", 
                           "Burlington", "Cambridge", "Greater Sudbury", "Guelph", 
                           "Hamilton", "Kitchener", "London", "Markham", "Mississauga", 
                           "Niagara Falls", "Norfolk County", "North Bay", "Oshawa", 
                           "Ottawa", "Peterborough", "Pickering", "Richmond Hill", 
                           "Sarnia", "Sault Ste. Marie", "St. Catharines", 
                           "Thunder Bay", "Toronto", "Vaughan", "Waterloo", "Welland", 
                           "Windsor"):
            new_location = input("Please enter a valid city: ")
        
        user.location = new_location

    
    print(f"Enter new interest(s). Previous interests will be erased. Leave blank to keep '{', '.join(user.interests)}'.")
    print('''   Enter interests one by one. Press enter after each. Enter STOP blank to stop adding.
        Select from the following list:
        Collecting, Clothing, Cooking, Gardening, Models, 
        Outdoors, Travelling, Fitness, Games, Sports, 
        Dancing, Music, Theater, Visual, Literary''')
    interest = input("New interest: ")
    if interest:
        new_interests = []
        while interest != "END":
            if interest in ("Collecting", "Clothing", "Cooking", "Gardening", "Models", "Outdoors", 
                            "Travelling", "Fitness", "Games", "Sports", "Dancing", "Music", "Theater", 
                            "Visual", "Literary"):
                new_interests.append(interest)
                interest = input("Add another interest: ")        
            else:
                interest = input("Please enter a valid interest: ")    
        
        user.interests = new_interests

    update_user(user)
    print("User profile updated successfully.")

def view_profile_list(user, users_list):
    print("\nPlease see your list of", users_list)
    if users_list == "likes":
        list_to_view = user.liked_users
    elif users_list == "dislikes":
        list_to_view = user.disliked_users
    elif users_list == "matches":
        list_to_view = user.matches

    if list_to_view: 
        for profile in list_to_view:
            print(fetch_user(profile))
    else:
        print("None!")
            

###### main app ######
def app():
    while True:
        print("\nWelcome to Pairfect!")
        print("1. Sign up")
        print("2. Log in")
        print("3. Exit")
        choice = input("Choose an option: ")
        
        if choice == '1':
            create_user()            
        elif choice == '2':
            user = login()
            if user:
                menu(user)
        elif choice == '3':
            print("Bye! Hope to see you soon!")
            break
        else:
            print("Invalid choice. Please try again.")

def menu(user):
    while True:
        print("\nMenu")
        print("1. View my profile")
        print("2. Update my profile")
        print("3. View all others' profiles")
        print("4. View my likes")
        print("5. View my dislikes")        
        print("6. View my matches")        
        print("7. Start matching")
        print("8. Delete my profile")
        print("9. Log out")
        choice = input("Choose an option: ")

        if choice == '1':
            view_one_profile(user.user_id)
        elif choice == '2':
            update_profile(user)
        elif choice == '3':
            view_all_profiles(user, 1) 
        elif choice == '4':
            view_profile_list(user, "likes")
        elif choice == '5':
            view_profile_list(user, "dislikes")
        elif choice == '6':
            view_profile_list(user, "matches")
        elif choice == '7':
            start_matching(user)
        elif choice == '8':
            delete_user(user.user_id)
            break
        elif choice == '9':
            print("Logged out successfully!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    app()
