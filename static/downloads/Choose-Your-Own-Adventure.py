#Jason Wacker
#CIS110
#Choose Your Own Adventure

#Greeting the user and providing instructions
print(f"Hello there! I have an exciting story about an adventurous dog. I can't wait to tell it.")

#Starting of the Nested Loop
keepGoing = "yes"
while keepGoing.lower() == "yes":

    #GContinuation of the user and providing instructions
    print(f"Before the story begins, I have a few questions I need you to answer.")
    print(f"After typing your answer, be sure to press the enter key.")
    print(f"\nPress the enter key to continue...")

    #Five Questions before the story begins
    dogName = input("\nWhat is the name of the adventurous dog? ")
    while len(dogName) == 0:
        dogName = input("The dogs name cannot be blank, please enter a name: ")

    dogBreed = input("\nWhat breed is the adventurous dog? ")
    while len(dogBreed) == 0:
        dogName = input("The dogs breed cannot be blank, please enter a breed: ")

    dogGender = input("\nWhat gender is the adventurous dog? boy or girl: ")
    while dogGender.lower() not in ["boy", "girl"]:
        dogGender = input("\nInvalid value! Please enter boy or girl: ")

    favoriteFood = input("\nWhat is your favorite food? ")
    while len(favoriteFood) == 0:
        favoriteFood = input("Your favorite cannot be blank, please enter a favorite food: ")

    dogfavoriteFood = input("\nWhat is the adventurous dog's favorite food? ")
    while len(dogfavoriteFood) == 0:
        dogfavoriteFood = input("The dogs favorite food cannot be blank, please enter a dogs favorite food: ")

    #The story begins
    print(f"\nLet's begin our story...")
    print(f"\nOur story begins in an empty office building on a sunny afternoon, just outside of Chicago.")
    print(f"There is an adventurous dog named {dogName}, who is also an anxious {dogBreed} dog who loves to investigate and is always looking for food.")
    print(f"Is today, the day?...Yes, it is Nosework class is today!")
    print(f"\n{dogName} has arrived at nose work class and is presented with two tasks: to find hidden scents in two different rooms.")
    print(f"{dogName} lines up at the start of the building and eagerly awaits the command...")
    print(f"\nFind it!")

    #Decision One
    print(f"\n{dogName} enters a room and discovers 12 shoe boxes laid out across the floor.")
    startsearchOne = input(f"\nShould {dogName} start sniffing the boxes? Type yes or no :")
    while startsearchOne.lower() != "yes" and startsearchOne.lower() != "no":
        startsearchOne = input("Please type yes or no: ")

    if startsearchOne == "yes":
        print(f"\n{dogName} starts sniffing each box one by one until they pass one with a very distinct smell. The scent is coming from a closet shoe box, and as they get closer, it grows stronger.")
        print(f"Certain that something is hidden inside; {dogName} confidently taps the box with their paw. Everyone cheers and {dogName} is rewarded with {dogfavoriteFood}.")
        print(f"{dogName} devours the {dogfavoriteFood} and continues down the hallway.")
    else:
        print(f"\n{dogName} hesitates and begins wandering around the room when suddenly the AC unit turns on, making a horrible noise.")
        print(f"Startled, {dogName} looks away from the boxes and continues down the hallway.")

    #Decision Two
    print(f"\n{dogName} enters a long, dimly lit hallway where six backpacks are lined up along the wall.")
    startsearchTwo = input(f"\nShould {dogName} start sniffing the backpacks? Type yes or no :")
    while startsearchTwo.lower() != "yes" and startsearchTwo.lower() != "no":
        startsearchTwo = input("Please type yes or no: ")

    if startsearchTwo == "yes":
        print(f"\n{dogName} starts sniffing each bag one at a time until their nose catches the unusual smell of {favoriteFood}.")
        print(f"Drawn in with excitement, {dogName} quickly zeros in on the bag containing the {favoriteFood}.")
        print(f"{dogName} taps the bag with their paw, and everyone cheers; it was {favoriteFood} all along!")
    else:
        print(f"\n{dogName} hesitates when they suddenly hear another dog barking in the distance.")
        print(f"The sound made them feel very anxious, and unable to continue, bringing {dogName} searches to an end.")

    #Alternative Endings
    if startsearchOne == "yes" and startsearchTwo == "yes":
        print(f"\nA round of cheers erupts through the building as {dogName} was scooped up and given a big hug.")
        print(f"They were praised as a good {dogGender} and rewarded with their favorite chew bone, ending the day as a true nose work champion.")
    elif startsearchOne == "no" and startsearchTwo == "no":
        print(f"\nEven though {dogName} wasn't able to complete either task today, their trainer scoops them up and gives them a big hug.")
        print(f"{dogName} is reassured that it's okay and that they will get them next time.")
        print(f"The crowd gives a warm round of applause as {dogName} is rewarded with a chew bone for their effort and bravery.")
    else:
        print(f"\nThe crowd erupts in cheers as {dogName} is scooped up and given a big hug.")
        print(f"They were praised as a good {dogGender} and gently reminded that it's okay not to find them all in one day, they will get them next time.")
        print(f"As a reward for their hard work and determination, {dogName} is given a well-earned chew bone to enjoy.")
    print(f"\nThe End")

    #Nested Loop to start the story over
    keepGoing = input("\nDo you want to start over? Enter yes or no: ")
    while keepGoing.lower() not in ["yes", "no"]:
        keepGoing = input("\nInvalid Value: Enter yes or no: ")