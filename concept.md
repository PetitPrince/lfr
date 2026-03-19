Witchard Looking for relation website
-------------------------------------

# Context
The "Witchards" association organizes live action roleplay (LARP) weekends themed around a magical school setting (called Czocha School of Wizardry) that's similar but legally distinct from Harry Potter's Hogwarts. This is a nordic style LARP, so there's no live combat with foam weapon (there are magical duel, but it's far from the central focus of the LARP) and emphasis is put on roleplay and character progression.

The players usually play as:
* students (vast majority)
* professor (selected few, usually experienced players)
* other staff such as janitor, assistant professor, etc. (happens when a player does not want to play as a student but is not confident enough to take the responsibility of professor; or the player have a specific idea)
* headmaster (special role that's discussed with the organizer)

This is a sandbox LARP. Although there are some pre-written characters (student, professors) this is merely a convenience for the player, as they are free to create whatever they want. Each character are still manually approved to avoid having Mary Sue / Marty Stu. While some players chose to make their character reappears from run to run, normally each run of the LARP is completely indepandent. 

Some things are fixed and cannot be changed by the players:
- Houses (Libussa, Faust, Molin, Durentius, Sendivogius)
- Teaching subjects (Alchemy, Arithmancy, Beastology, Conflux Studies, Herbology, Invocation, Magical Theory, Magical Defence, Mind Magic, Ritual Magic, Runic Magic,  Technomancy)
- Path (determines what the student teach): Artificier, Cryptozoologist, Curse Breakers, Guardian, Healers
- The grade/year a student is in: 1st year (Junior), 2nd year (Sophomore), 3rd Year (Senior)
- For each house, one or two 3rd year takes the role of Prefects
- Clubs: Ancient Order of Mischief (pranking club), A.R.M. (hexist club), W.A.N.D. (anti-hexist club), Horse without Wings (poetry), Duelling club (high class duelling), Fight club (low class duelling), Iron Covenent (illegal magic)
- Some lore details that are important for the characters, but have no structural important for the LARP:
	- Blood status: Hexborn, mundane
	- Existing other schools that the student attended to before coming to Czocha

The way the LARP is organized is as follow:
1. A player volunteers to be headmaster. They discuss with the organizers about the theme and vibes of the run, and specific mechanics if application.
2. Casting: regular players buy the tickets. The tickets comes with a questionnaire that asks if they want to be a professor or a student. If professor: what teaching subject. If student: what they are looking for in term of experience (adventure, puzzle solving, teenage drama, ...), what year they want to be in, what path they want to be in, what house they want to be in (only for sophomores and seniors). The organizers decides who go where
3. Looking for Relation (LFR) pre-game: 
	- Players post on a central place a "Lookin for relation" post. This post describe the characters the player will play. The goal is for other players to know the character (some are supposed to be classmates, housemates, etc.), and if need be discuss about further relationships (best friends, rivals, lovers, member of the same family, etc...). This is also a way to signpost what the player is looking in term of gameplay ("I want my character to be bullied !", "I play as a mentor type !"etc.). 
	- This is also the place to announce extracurricular activities ("Conflux Studies Extracurricular on Friday in the Marble Hall for every student interested in legally gray magic !"), school-wide plotting ("my character is a prankster and will put minor curses everywhere in the castle in form of paper fishes", "The Froissard de Bersaillin Notary office will fund a scholarship for mundaneborn during the game. Please contact me for details.") and club recruitment (not all )
	- Since those post are usually done in a private Facebook group or in a Discord forum, the format of the text is very free-form.
	- Players usually post pictures of their character (player in costume) alongside the LFR
4.  Game ! The LARP is played at Czocha castle.


# Goal of the project
Make a web app for the players and organizers so that the "Looking for relation" post is facilitated compared to Facebook Group / Discord, and out of those platform. 

Mandtory feature:
* Being able to post LFR
* Filter LFR so that players can search for players they will most likely play with (typically a player would look for a player in the same house or same year or same path, ...)
* Being able to comment to a LFR to express interest

Ideally, this project could also be adapated for a sister-event of Czocha (called Bothwell) that have very similar overall mechanics but with some notable differences (no prefect for instance, and a new class of student that's modelled after a PhD student). 

# Tech stack
* Backend: Django, because that's what I'm familiar with. Also it's boring and robust.
* Frontend: ???