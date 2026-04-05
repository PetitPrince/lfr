"""Seed 125 additional student castings + character posts for the active run."""
import random

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from casting.models import Casting
from posts.models import LookingForEntry, Post, PostKeyword, Rumor

# fmt: off
CHARACTERS = [
    # (name, content, keywords, looking_for[(label, desc)], rumors)
    ("Leila Hakim (she/her)",
     "Leila grew up in a family of wandmakers and has an almost unsettling intuition for what kind of wand suits a person. She'll size you up in thirty seconds and tell you things about yourself you haven't admitted yet. Quiet, watchful, and unnervingly perceptive — she makes people nervous without meaning to. She doesn't have many friends, but the ones she has would walk through fire for her.",
     ["Perceptive", "Quiet", "Loyal", "Mysterious"],
     [("Friends", "Leila doesn't make friends easily, but she's looking for people who don't mind long silences."),
      ("Rivals", "Someone who thinks they can read people better than she can.")],
     ["They say Leila can tell if you're lying just by holding your wand.", "Her family's workshop was raided by the authorities last year. Nobody knows why."]),

    ("Jasper Krol (he/him)",
     "Jasper is the kind of person who knows everyone's name and nobody's secrets — or so he claims. He runs an underground newspaper called *The Whisper* that publishes school gossip, political commentary, and the occasional recipe. He's charming, evasive, and always taking notes. People love him until they end up in one of his articles.",
     ["Journalist", "Charming", "Cunning", "Outgoing"],
     [("Sources", "Jasper is always looking for people willing to share information — on or off the record."),
      ("Enemies", "Someone who got burned by a Whisper article and wants revenge.")],
     ["The Whisper is funded by someone outside the school.", "Jasper's real name might not be Jasper."]),

    ("Maren Solberg (she/her)",
     "Maren arrived from Scandinavia with a trunk full of rune stones and a deep suspicion of institutional magic. She thinks the school curriculum is **dangerously incomplete** and has been petitioning professors to include elder traditions. She's brilliant, argumentative, and completely exhausting to debate. Underneath the academic intensity, she's surprisingly gentle with younger students.",
     ["Intellectual", "Rebellious", "Passionate", "Mentor"],
     [("Study Buddy", "Someone who wants to learn real magic, not textbook magic."),
      ("Debate Partner", "Maren needs someone who can actually keep up.")],
     ["Maren's grandmother was a völva — a genuine Norse seeress.", "She supposedly corrected a professor's research paper. In red ink."]),

    ("Oliver Chen (he/him)",
     "Oliver has a plan. Actually, Oliver has **seventeen plans**, colour-coded and cross-referenced. He's running for student representative, organising the charity gala, and somehow still maintaining perfect grades. People either admire his ambition or find it exhausting. He'd say both reactions are valid. Deep down, Oliver is terrified of what happens if he ever stops moving.",
     ["Ambitious", "Leader", "Perfectionist", "Anxious"],
     [("Campaign Team", "Oliver needs allies for his student representative campaign."),
      ("Friends", "Real ones, not strategic ones. He's trying to learn the difference.")],
     ["Oliver hasn't slept more than four hours a night since September.", "His family expects him to enter politics after graduation."]),

    ("Tova Lindgren (she/they)",
     "Tova communicates primarily through art. Their dorm room is covered in murals that change depending on who's looking at them. They rarely speak in class but their essays are so beautiful that Professor Thornwick once read one aloud — which mortified Tova entirely. They're looking for people who understand that silence can be a form of conversation.",
     ["Artistic", "Shy", "Dreamer", "Mysterious"],
     [("Muse", "Tova is looking for someone interesting enough to paint."),
      ("Friends", "People who are comfortable with long, quiet afternoons.")],
     ["Tova's paintings have been known to move when no one is watching.", "They supposedly painted something so disturbing it had to be locked away."]),

    ("Rashid Al-Farsi (he/him)",
     "Rashid transferred in from a school in the desert where magic is woven into song. He finds European wand-waving quaint but charming. He's warm, musical, and surprisingly homesick, though he hides it behind jokes and an impressive collection of magical instruments. He can usually be found in the courtyard, playing something melancholy and pretending it's upbeat.",
     ["Musical", "Cheerful", "Homesick", "Outgoing"],
     [("Band", "Rashid wants to start a magical music group. Talent optional, enthusiasm mandatory."),
      ("Friends", "Anyone who'll sit and listen to music with him.")],
     ["Rashid's songs can affect people's emotions — literally.", "He left his old school under circumstances he won't discuss."]),

    ("Ingrid Voss (she/her)",
     "Ingrid's family has produced Guardian-path graduates for seven generations, and she intends to be the eighth. She trains before dawn, studies combat theory after dinner, and has opinions about protective ward configurations that she will share whether you ask or not. She's intense, honourable, and secretly writes poetry that she shows absolutely no one.",
     ["Athletic", "Disciplined", "Loyal", "Intense"],
     [("Training Partner", "Someone who takes physical conditioning as seriously as she does."),
      ("Rivals", "A worthy opponent for the duelling tournament.")],
     ["Ingrid once disarmed three seniors simultaneously during a practice duel.", "Her poetry notebook is warded with magic that causes temporary blindness."]),

    ("Samuel Okafor (he/him)",
     "Samuel's gift is with magical creatures. He can calm a distressed griffin, negotiate with a territorial niffler, and has been banned from the school menagerie twice for 'unauthorised befriending.' He's gentle, patient, and slightly feral around the edges. He'd rather spend time with animals than most humans, but he's trying to be more social this year.",
     ["Kind", "Loner", "Adventurous", "Patient"],
     [("Fellow Creature Lovers", "Samuel wants to meet others who understand that animals are people too."),
      ("Mentor", "Someone to help him navigate... human social situations.")],
     ["Samuel sleeps in the menagerie at least twice a week.", "A phoenix supposedly chose to land on his shoulder during the opening ceremony."]),

    ("Clara Dupont (she/her)",
     "Clara comes from old money and wants everyone to know it — and simultaneously wants everyone to know she doesn't care about it. She's contradictory, dramatic, and genuinely trying to be a better person than her upbringing suggests. She throws the best parties, makes the worst decisions, and apologises with expensive gifts. People keep forgiving her.",
     ["Dramatic", "Rich", "Kind", "Impulsive"],
     [("Party Committee", "Clara is planning the social event of the year and needs help."),
      ("Ex-friends", "Someone who got tired of Clara's chaos and walked away.")],
     ["The Dupont family donated an entire wing of the library. With conditions.", "Clara was expelled from her previous school. Her parents bought her way into this one."]),

    ("Mikkel Brandt (he/him)",
     "Mikkel is the person you go to when you need something fixed — a broken wand, a malfunctioning spell, a friendship. He's practical, steady, and aggressively normal in a school full of eccentrics. He runs the Artificer workshop's open hours and has a reputation for being the most reliable person in any room. He finds this reputation both flattering and suffocating.",
     ["Reliable", "Nerdy", "Kind", "Practical"],
     [("Friends", "Mikkel wants friends who see him as a person, not a service."),
      ("Romantic Interest", "He's had a crush on someone for two years and done absolutely nothing about it.")],
     ["Mikkel fixed an artifact that three professors had declared unfixable.", "He's been offered apprenticeships by two different master artificers."]),

    ("Yuki Sato (she/her)",
     "Yuki arrived this year with a scholarship and a chip on her shoulder. She's from a non-magical family and has to work twice as hard to keep up — which she does, spectacularly. She's fierce, independent, and exhausted by people who take magic for granted. She has zero patience for pureblood politics and will tell you so to your face.",
     ["Ambitious", "Rebellious", "Athletic", "Proud"],
     [("Study Group", "Yuki needs people who actually study, not people who coast on family magic."),
      ("Allies", "Other mundaneborns who are tired of the status quo.")],
     ["Yuki outperformed every legacy student on the entrance exam.", "She supposedly turned down an offer to transfer to a more prestigious school."]),

    ("Fabian Richter (he/him)",
     "Fabian is the boy who sits at the back, hood up, headphones in, and somehow still aces every exam. He's a sleepwalker — literally and metaphorically. Magic comes effortlessly to him and he finds this profoundly boring. He's looking for something, anything, that makes him feel awake. People think he's cool. He thinks he's empty.",
     ["Mysterious", "Intellectual", "Loner", "Brooding"],
     [("Someone Interesting", "Fabian is looking for a person or cause that actually makes him care about something."),
      ("Rivals", "Someone who can beat him at something. Anything. Please.")],
     ["Fabian cast a spell in his sleep that turned the entire dormitory ceiling into a night sky.", "He's been offered remedial 'motivation counselling' by three different professors."]),

    ("Nia Osei (she/her)",
     "Nia is studying healing magic with the focus of a surgeon and the bedside manner of a hurricane. She's blunt, efficient, and cares so deeply about her patients that she sometimes forgets to care about their feelings. She runs a free clinic for students who don't want to go to the official infirmary — no questions asked, strict confidentiality.",
     ["Healer", "Blunt", "Kind", "Disciplined"],
     [("Clinic Volunteers", "Nia needs help running the student clinic. Medical interest preferred but not required."),
      ("Friends", "People who can handle honesty without getting offended.")],
     ["Nia has treated injuries that should have been reported to the administration.", "She keeps a locked journal of every patient she's ever treated."]),

    ("Leon Wolff (he/him)",
     "Leon's family are werewolves — the kind that assimilated into wizarding society and don't talk about the full moon. Leon is tired of not talking about it. He's started a support group for students with 'non-standard magical conditions' and has become an unexpected activist. He's warm, angry, and trying to figure out how to be both at the same time.",
     ["Activist", "Passionate", "Kind", "Conflicted"],
     [("Support Group", "Leon's group meets every Thursday. All conditions welcome, no judgement."),
      ("Allies", "People who want to push for policy changes around non-human heritage rights.")],
     ["Leon's condition is an open secret that he's trying to make just... open.", "His family has reportedly threatened to disown him for his activism."]),

    ("Astrid Magnusson (she/her)",
     "Astrid is a third-generation Curse-Breaker who has already seen more ancient tombs than most graduates. Her parents take her on expeditions during holidays and she has the scars to prove it. She's fearless, reckless, and tells the best stories at dinner. She's also failing Arithmancy because she finds numbers 'spiritually oppressive.'",
     ["Adventurous", "Reckless", "Outgoing", "Storyteller"],
     [("Expedition Partners", "Astrid is planning an unsanctioned trip to the ruins beneath the school. Who's in?"),
      ("Tutor", "Someone who can make Arithmancy make sense. She's desperate.")],
     ["Astrid found something in the school's catacombs that she won't talk about.", "Her parents' expeditions may not be entirely legal."]),

    ("Hugo Perreira (he/him)",
     "Hugo is a competitive duellist who treats every interaction like a chess match. He's calculating, patient, and devastatingly polite. He comes from a family of diplomats and has been raised to never show his hand. People find him either fascinating or infuriating — he considers both outcomes acceptable. He has a secret sweet tooth and an extensive tea collection.",
     ["Strategic", "Polite", "Competitive", "Mysterious"],
     [("Duelling Partners", "Hugo is always looking for worthy opponents. He'll even teach you, if you ask nicely."),
      ("Political Allies", "The student council elections are approaching. Hugo has plans.")],
     ["Hugo has never lost a formal duel. Some say he's never even been touched.", "His family has connections to the Ministry that go very, very deep."]),

    ("Petra Novak (she/her)",
     "Petra runs the Drama Club with the intensity of a military campaign. She writes, directs, and occasionally stars in productions that are equal parts magical spectacle and scathing social commentary. She's theatrical in every sense — she once delivered a breakup speech in iambic pentameter. Off stage, she's surprisingly insecure.",
     ["Dramatic", "Creative", "Leader", "Insecure"],
     [("Actors", "The Drama Club is casting for the winter production. All talent levels welcome."),
      ("Writers", "Petra needs a co-writer who can handle criticism. And dish it out.")],
     ["Petra's last production was almost shut down for 'subversive content.'", "She writes letters to someone she's never met."]),

    ("Kai Eriksson (they/them)",
     "Kai doesn't fit neatly into any box and has stopped trying. They study a bit of everything — healing, curses, artificing — and are mediocre at all of it, which they find liberating. They run the school radio station from a converted broom closet and have the best taste in music of anyone you'll ever meet. They're the person everyone likes but nobody knows well.",
     ["Eclectic", "Musical", "Outgoing", "Evasive"],
     [("Radio Contributors", "The station needs DJs, reporters, and someone who can fix the transmitter."),
      ("Friends", "Kai wants to actually let someone in this year.")],
     ["Nobody knows where Kai goes on weekends.", "The radio station has been picking up strange transmissions from somewhere beneath the school."]),

    ("Dahlia Morozova (she/her)",
     "Dahlia's grandmother was a famous dark magic researcher — emphasis on *was*, before the academic community turned on her. Dahlia is here to rehabilitate the family name through legitimate scholarship, but she can't help being fascinated by the same forbidden topics. She's brilliant, secretive, and deeply paranoid that people are judging her by her surname.",
     ["Intellectual", "Paranoid", "Ambitious", "Secretive"],
     [("Research Partners", "Dahlia is working on a thesis about the ethics of restricted magic. She needs collaborators who won't judge."),
      ("Friends", "People who see Dahlia, not Morozova.")],
     ["Dahlia has been seen in the restricted section of the library after hours.", "Her grandmother's banned research papers supposedly contain genuine breakthroughs."]),

    ("Emeka Adeyemi (he/him)",
     "Emeka is the captain of the Fireball Dragon Club and takes the sport with a seriousness that borders on religious. He's loud, competitive, and the most loyal teammate you'll ever have. Off the pitch, he's studying to be a healer — the juxtaposition confuses people. He says breaking things and fixing things require the same understanding of structure.",
     ["Athletic", "Leader", "Loud", "Loyal"],
     [("Team Members", "Fireball Dragon Club is recruiting. Tryouts are open but Emeka's standards are high."),
      ("Study Buddy", "Healing theory is harder than it looks. Emeka needs help with the theory side.")],
     ["Emeka turned down a professional sports offer to stay in school.", "He's been secretly learning combat magic to protect his teammates."]),

    ("Linnea Holm (she/her)",
     "Linnea talks to plants. Not in the 'I'm a quirky botanist' way — in the 'the plants talk back' way. She's been this way since childhood and it took her parents a long time to believe her. She's sweet, earnest, and a little odd. Her dorm room is a jungle and her best friend is a sentient fern named Margareta.",
     ["Kind", "Eccentric", "Shy", "Dreamer"],
     [("Fellow Plant Lovers", "Linnea wants to meet people who take botanical magic seriously."),
      ("Friends", "Anyone who won't make fun of Margareta.")],
     ["Margareta the fern has been growing at an alarming rate.", "Linnea once stopped a magical wildfire by asking the trees nicely."]),

    ("Anton Kovac (he/him)",
     "Anton is a scholarship student from a mining town where magic is considered a practical trade, not an art form. He finds the school's emphasis on theory and tradition baffling. He can repair a ward in half the time of any other student but can't write a proper essay to save his life. He's proud, stubborn, and increasingly angry about the class divide he sees everywhere.",
     ["Practical", "Proud", "Rebellious", "Working-class"],
     [("Allies", "Other students who think the school caters too much to old money."),
      ("Tutor", "Someone who can help with essays without being condescending about it.")],
     ["Anton built a functioning magical device from scrapyard parts.", "He's been writing anonymous letters to the school board about scholarship inequality."]),

    ("Camille Beaumont (she/her)",
     "Camille is a hexborn from a prestigious family who desperately wishes she were interesting. She's pleasant, well-mannered, well-connected, and bored out of her mind. This year she's decided to reinvent herself, which so far has involved a dramatic haircut, an interest in Curse-Breaking, and befriending the most chaotic people she can find.",
     ["Bored", "Rich", "Adventurous", "Naive"],
     [("Bad Influences", "Camille wants to meet people her parents would disapprove of."),
      ("Adventure Partners", "She wants to do something she'll actually remember.")],
     ["Camille's family is quietly furious about her sudden personality change.", "She's been seen leaving the school grounds at night."]),

    ("Tomasz Wójcik (he/him)",
     "Tomasz is the school's unofficial bookie. He'll take bets on duelling outcomes, exam results, romantic developments, and whether the cafeteria will serve fish on Friday. He's entrepreneurial, morally flexible, and genuinely convinced he's providing a valuable service. He's also surprisingly good at Arithmancy — for obvious reasons.",
     ["Cunning", "Entrepreneurial", "Cheerful", "Amoral"],
     [("Business Partners", "Tomasz is expanding operations and needs help. Discretion required."),
      ("Clients", "Got a prediction you're confident about? Tomasz will give you good odds.")],
     ["Tomasz made more money last term than some professors.", "The administration has been trying to catch him for two years."]),

    ("Saoirse Murphy (she/her)",
     "Saoirse is haunted. Not metaphorically — she can see and communicate with ghosts, and they won't leave her alone. She's been dealing with this since she was seven and has developed a dry, dark sense of humour about it. She's tough, sarcastic, and secretly lonely because most people find her ability unsettling. She's studying to be a Curse-Breaker because ghosts and curses tend to overlap.",
     ["Sarcastic", "Tough", "Lonely", "Perceptive"],
     [("Friends", "Saoirse needs people who won't freak out when she talks to empty corners."),
      ("Research Partners", "She's investigating a ghost that's been haunting the east tower. Help wanted.")],
     ["The ghost in the east tower has been getting more agitated since Saoirse arrived.", "She supposedly held a full conversation with the school's founder."]),

    ("Henrik Larsson (he/him)",
     "Henrik is the quiet kid who sits in the library and reads books about military history. Not magical military history — mundane military history. He's fascinated by strategy, logistics, and the art of war. He applies these principles to everything: academic planning, social navigation, even the way he organises his desk. People find him slightly unsettling. He finds them slightly inefficient.",
     ["Strategic", "Quiet", "Intellectual", "Peculiar"],
     [("Chess Club", "Henrik runs an informal strategy games club. Attendance is... sparse."),
      ("Study Group", "He needs people who take academic planning seriously.")],
     ["Henrik has a map of the entire school with tactical annotations.", "He predicted the outcome of last year's student elections with eerie accuracy."]),

    ("Priya Sharma (she/her)",
     "Priya's parents are both healers and she was supposed to follow in their footsteps. Instead, she's discovered a passion for Ritual Magic that horrifies her traditionalist family. She's torn between duty and desire, which makes her simultaneously the most dedicated student in her required courses and the most passionate student in her forbidden ones.",
     ["Conflicted", "Passionate", "Intellectual", "Rebellious"],
     [("Fellow Ritual Students", "Priya wants to connect with others who take Ritual Magic seriously."),
      ("Family Drama", "Anyone else dealing with parents who don't understand their choices?")],
     ["Priya performed a ritual that lit up the entire courtyard. Accidentally.", "Her parents have been sending increasingly concerned owls."]),

    ("Max Hoffman (he/him)",
     "Max is an aspiring magical chef who somehow ended up at a school for wizards instead of a culinary academy. He's convinced that cooking and potion-making are the same discipline (he's not entirely wrong) and runs an illegal kitchen in the basement where he hosts invite-only dinners. He's generous, eccentric, and his brownies might be slightly enchanted.",
     ["Creative", "Generous", "Eccentric", "Cheerful"],
     [("Dinner Guests", "Max's underground supper club meets monthly. Bring your own plate."),
      ("Ingredient Foragers", "He needs people who can source unusual magical ingredients. Legally, preferably.")],
     ["Max's food has been known to cause unexpected emotional reactions.", "The potions professor is suspiciously interested in Max's recipes."]),

    ("Elena Vasquez (she/her)",
     "Elena is a mundaneborn who discovered magic at age 15 — late, by wizarding standards. She's playing catch-up and handling it with a fierce, stubborn grace that impresses her professors. She treats every lesson like a gift and every setback like a personal challenge. She's optimistic, hardworking, and sometimes painfully earnest.",
     ["Optimistic", "Hardworking", "Earnest", "Brave"],
     [("Study Buddy", "Elena is behind on three years of magical theory and needs all the help she can get."),
      ("Friends", "She wants to meet people who remember what it felt like to discover magic for the first time.")],
     ["Elena's mundane family thinks she's at a boarding school for gifted students.", "She mastered a spell in one day that takes most students a month."]),

    ("Felix Engström (he/him)",
     "Felix is the school's resident conspiracy theorist. He believes the administration is hiding something (they probably are), that the curriculum is propaganda (it might be), and that the school was built on a site of ancient magical significance (this one's actually true). He's brilliant, paranoid, and writes a column for The Whisper called 'What They Don't Want You To Know.'",
     ["Paranoid", "Intellectual", "Rebellious", "Nerdy"],
     [("Truth Seekers", "Felix has evidence of administrative cover-ups. He needs people who aren't afraid to dig."),
      ("Sources", "Anyone with access to restricted areas or faculty meetings.")],
     ["Felix's dorm room is covered in connected string and newspaper clippings.", "He was right about the cafeteria scandal. Nobody apologised."]),

    ("Aisha Ndiaye (she/her)",
     "Aisha is a natural-born mediator. She can walk into any argument and have both sides feeling heard within ten minutes. This makes her invaluable during house conflicts, popular at parties, and absolutely miserable inside, because she absorbs everyone's problems and never addresses her own. She's studying Guardian path because protecting people is the only thing that feels real.",
     ["Empathetic", "Leader", "Selfless", "Exhausted"],
     [("Friends", "Aisha needs people who ask how *she's* doing for once."),
      ("Co-mediators", "The school needs a proper peer mediation system. Help her build one.")],
     ["Aisha hasn't cried in two years. She considers this a problem.", "She turned down a house leadership position because she didn't trust herself with the power."]),

    ("Bjorn Svensson (he/him)",
     "Bjorn looks like he was grown in a gymnasium and educated in a library. He's enormous, gentle, and deeply intellectual — a combination that confuses people. He writes papers on the philosophical implications of transformation magic and can bench-press a small dragon. He's soft-spoken, thoughtful, and gets very upset about logical fallacies.",
     ["Intellectual", "Athletic", "Kind", "Gentle"],
     [("Philosophy Club", "Bjorn is starting a magical philosophy discussion group. Snacks provided."),
      ("Training Partner", "He needs someone to spot him at the gym who can also discuss Kierkegaard.")],
     ["Bjorn once stopped a fight between two seniors just by standing up.", "His philosophy paper was published in an academic journal under a pseudonym."]),

    ("Iris Papadopoulos (she/her)",
     "Iris can see magical auras — the energy signatures that surround people, places, and objects. It's beautiful and overwhelming and she's still learning to control it. Sometimes she stares at people too long because their aura is doing something interesting. She's awkward, brilliant, and completely hopeless at small talk. She's studying to become a Healer because aura reading has obvious diagnostic applications.",
     ["Perceptive", "Awkward", "Intellectual", "Dreamer"],
     [("Research Partners", "Iris wants to map the school's magical energy patterns. She needs help with the boring parts."),
      ("Patient Friends", "People who don't mind being stared at occasionally.")],
     ["Iris can apparently tell when someone is lying by the colour of their aura.", "She once diagnosed a curse that the school healer missed."]),

    ("Rafael Santos (he/him)",
     "Rafael is a third-year who has reinvented himself every single year. First year: shy bookworm. Second year: party animal. This year: aspiring political leader. Nobody knows which version is the real Rafael, including Rafael. He's running for student council on a platform of 'radical transparency' which is ironic given that he's the least transparent person in school.",
     ["Chameleon", "Ambitious", "Charming", "Insecure"],
     [("Campaign Staff", "Rafael's student council campaign needs volunteers. The platform is still... evolving."),
      ("Old Friends", "People who knew first-year Rafael and miss him.")],
     ["Rafael's family moved countries three times before he started school.", "Each of his reinventions coincided with something he won't talk about."]),

    ("Maja Kristiansen (she/her)",
     "Maja is nocturnal by nature and preference. She does her best thinking between midnight and 4am, attends morning classes like a sleepwalker, and has turned her circadian dysfunction into an aesthetic. She's a talented astronomer and divination student who maps the night sky with obsessive precision. She claims the stars told her something important last month but won't say what.",
     ["Nocturnal", "Mysterious", "Intellectual", "Artistic"],
     [("Stargazing Companions", "Maja leads midnight observation sessions on the astronomy tower. Bring blankets."),
      ("Divination Students", "She's working on a new predictive model and needs people to test it on.")],
     ["Maja hasn't seen a sunrise in six months. By choice.", "The astronomy professor has started consulting her instead of the other way around."]),

    ("James MacAllister (he/him)",
     "James is the fourth MacAllister to attend this school, and each one has been more of a disaster than the last. James is continuing the tradition admirably. He's well-meaning, accident-prone, and cursed with the family gift of accidentally setting things on fire. He's cheerful about it in a way that concerns the fire safety officer.",
     ["Clumsy", "Cheerful", "Loyal", "Disaster-prone"],
     [("Fire Brigade", "James is forming a student fire response team. For completely unrelated reasons."),
      ("Friends", "People who own fireproof clothing.")],
     ["The MacAllister family has donated seventeen fire extinguishers to the school.", "James's grandfather holds the record for most accidental fires in a single semester. James is close to breaking it."]),

    ("Song-Yi Park (she/her)",
     "Song-Yi is a prodigy who was casting complex spells before she could read. She skipped a year and is now the youngest student in most of her classes, which she handles with a maturity that makes everyone uncomfortable. She's polite, controlled, and under enormous pressure from a family that considers anything less than excellence to be failure. She collects pressed flowers and tells no one.",
     ["Prodigy", "Perfectionist", "Mature", "Lonely"],
     [("Mentor", "Song-Yi would never admit it, but she needs someone older to talk to."),
      ("Friends", "People who treat her like a person, not a specimen.")],
     ["Song-Yi's family has already planned her career through age forty.", "She was seen crying in the greenhouse. She told everyone it was allergies."]),

    ("Anders Dahl (he/him)",
     "Anders is the kind of person who brings soup when you're sick and threatens violence when someone is mean to his friends. He's a walking contradiction: soft-hearted and short-tempered, nurturing and aggressive, the best cook in the dorms and the worst diplomat in any argument. He's studying the Guardian path because he wants to protect people. He just hasn't figured out how to protect them calmly.",
     ["Protective", "Hot-headed", "Kind", "Loyal"],
     [("People to Protect", "Anders has decided you're his responsibility now. Don't argue."),
      ("Anger Management", "He's looking for ways to channel his temper constructively. Suggestions welcome.")],
     ["Anders punched a wall last term and the wall cracked. The wall was stone.", "He brings homemade cookies to the infirmary every week."]),

    ("Celeste Moreau (she/her)",
     "Celeste is from a long line of seers, and she'd like everyone to know that real divination is nothing like the 'parlour tricks' taught in class. She sees fragments of possible futures — never complete, never certain, always disturbing. She's dramatic, intense, and occasionally genuinely terrifying when she drops into a trance mid-conversation. She insists it's not as dramatic as it looks.",
     ["Seer", "Dramatic", "Intense", "Mysterious"],
     [("Believers", "Celeste wants to connect with people who take prophecy seriously."),
      ("Skeptics", "She also wants to prove the doubters wrong.")],
     ["Celeste predicted the library flood three weeks before it happened.", "She keeps a journal of predictions. The accuracy rate is reportedly unsettling."]),

    ("Eamon O'Brien (he/him)",
     "Eamon is a halfblood from a family of magical musicians. He plays the fiddle, the pipes, and something he built himself that he calls a 'resonance amplifier.' He believes music is the oldest form of magic and is frustrated that the curriculum barely acknowledges it. He's passionate, hot-headed, and will play at any gathering, invited or not.",
     ["Musical", "Passionate", "Rebellious", "Outgoing"],
     [("Band", "Eamon is forming a band. He's already written twelve songs. They need an audience."),
      ("Faculty Allies", "He's petitioning for a music magic elective and needs professor support.")],
     ["Eamon's music caused a spontaneous dance at last year's feast.", "His 'resonance amplifier' has been confiscated twice and keeps reappearing."]),

    ("Wei Lin (she/her)",
     "Wei Lin arrived two months late due to 'visa complications' that she refuses to elaborate on. She's catching up fast, speaks four languages, and has a working knowledge of three different magical traditions. She's adaptable, guarded, and watching everything with the careful attention of someone who's learned to read rooms for survival, not curiosity.",
     ["Adaptable", "Guarded", "Intellectual", "Perceptive"],
     [("Study Group", "Wei Lin needs to catch up quickly and wants dedicated study partners."),
      ("Friends", "People who don't ask too many questions about where she came from.")],
     ["Wei Lin's previous school doesn't appear in any official records.", "She speaks to her family in a language no one at school can identify."]),

    ("Nikolai Petrov (he/him)",
     "Nikolai is royalty. Not magical royalty — actual mundane royalty, from a minor Eastern European house that happens to also be magical. He finds the collision of his two worlds endlessly complicated. He's formal, generous, and deeply uncomfortable with the concept of being 'normal.' He tips his hat to professors and calls everyone by their surname until told otherwise.",
     ["Formal", "Generous", "Awkward", "Kind"],
     [("Friends", "Nikolai wants to learn how normal people befriend each other."),
      ("Cultural Exchange", "He's fascinated by how different backgrounds approach magic.")],
     ["Nikolai arrived with a personal valet. The valet was sent home.", "His family's castle is supposedly built on a convergence of magical ley lines."]),

    ("Freya Andersen (she/her)",
     "Freya is an environmental activist who believes magical society is destroying natural magical ecosystems. She chains herself to endangered magical trees, campaigns against unethical potion ingredient sourcing, and is generally considered a nuisance by the administration. She's fierce, idealistic, and funded by an anonymous donor she's never met.",
     ["Activist", "Fierce", "Idealistic", "Rebellious"],
     [("Activists", "Freya's environmental group needs more members. The planet is literally on fire."),
      ("Enemies", "People who profit from magical exploitation. She's keeping a list.")],
     ["Freya's anonymous donor may have ulterior motives.", "She found a magical species in the school forest that shouldn't exist here."]),

    ("Lucas Hartmann (he/him)",
     "Lucas failed his first year and is repeating it, which he handles with a cheerful acceptance that baffles his professors. He's not stupid — he's distracted, disorganised, and was dealing with a family crisis that he told exactly zero adults about. He's back now, more focused, and determined to prove he belongs here. He's also the best chess player in school.",
     ["Resilient", "Cheerful", "Disorganised", "Strategic"],
     [("Study Buddy", "Lucas is actually trying this time and wants accountability partners."),
      ("Chess Opponents", "He's undefeated and getting bored. Challenge him.")],
     ["Lucas's family crisis involved magical law enforcement.", "He solved a puzzle in the restricted library that hadn't been solved in fifty years."]),

    ("Amara Okonkwo (she/her)",
     "Amara is a born leader who hasn't decided what to lead yet. She's the person who organises study groups, mediates disputes, and somehow always ends up in charge of things she didn't volunteer for. She's capable, charismatic, and terrified that she's only good at managing other people's problems because she can't face her own.",
     ["Leader", "Charismatic", "Capable", "Evasive"],
     [("Right Hand", "Amara needs a deputy. Someone who can tell her when she's wrong."),
      ("Friends", "People who see through the competence to the mess underneath.")],
     ["Amara turned down every official leadership position offered to her.", "She keeps a list of everyone she's ever let down."]),

    ("Erik Johansson (he/him)",
     "Erik is unremarkable in every measurable way — average grades, average magical talent, average social skills. He's made peace with this. What people don't know is that Erik has a photographic memory and has been quietly memorising everything: every spell, every conversation, every secret. He's building a map of the school's social landscape and he's not sure why yet.",
     ["Quiet", "Observant", "Average", "Secretive"],
     [("Someone to Trust", "Erik has a lot of information and nobody to share it with."),
      ("Purpose", "He needs to figure out what to do with everything he knows.")],
     ["Erik can recite any conversation he's overheard verbatim.", "He knows things about people that he shouldn't possibly know."]),

    ("Zoe Fischer (she/her)",
     "Zoe is a synesthete — she experiences magic as colour, taste, and sound simultaneously. Every spell has a flavour, every ward has a melody, and exam season tastes like burnt toast. She's learning to use this as an analytical tool rather than a disability. She's bright, overwhelmed, and trying to write a thesis on 'Multi-Sensory Magical Perception' that her advisor doesn't fully understand.",
     ["Synesthetic", "Intellectual", "Overwhelmed", "Creative"],
     [("Research Subjects", "Zoe needs volunteers willing to cast spells while she takes notes on how they taste."),
      ("Sensory Friends", "Other people who experience magic differently.")],
     ["Zoe can identify potions by their 'sound' without seeing them.", "She once described a professor's spell as 'the colour of a dying sunset' and the professor didn't speak to her for a week."]),

    ("Ibrahim Hassan (he/him)",
     "Ibrahim is the student everyone goes to for advice, not because he's wise, but because he listens. Really listens. He asks questions instead of giving answers and somehow you walk away feeling like you solved your own problem. He's studying the Healer path because he believes emotional healing is as important as physical. He makes excellent tea and terrible jokes.",
     ["Empathetic", "Patient", "Wise", "Humorous"],
     [("Tea and Talk", "Ibrahim hosts informal tea sessions. Bring your problems, leave with clarity. Or at least good tea."),
      ("Healer Students", "He wants to connect with others who take the emotional side of healing seriously.")],
     ["Ibrahim was a peer counsellor at his previous school. He left because of burnout.", "His tea collection includes leaves that are technically classified as controlled substances."]),

    ("Lena Schmidt (she/her)",
     "Lena is a competitive perfectionist who expresses affection through academic rivalry. She will proofread your essay, point out every flaw, and then stay up all night helping you fix them. She's prickly, brilliant, and secretly the most loyal person you'll ever meet. She's top of her class and hates that this is the most interesting thing most people know about her.",
     ["Perfectionist", "Competitive", "Loyal", "Prickly"],
     [("Academic Rivals", "Lena wants someone who can push her academically. She's stagnating."),
      ("Real Friends", "Not networking contacts. Not study partners. Actual friends.")],
     ["Lena reportedly stayed awake for 72 hours during exam week last year.", "She writes anonymous encouraging notes and slips them under people's doors."]),

    ("Oscar Müller (he/him)",
     "Oscar is a gentle giant who breeds magical butterflies. His greenhouse is full of them — each one unique, some capable of carrying small messages, others that change colour with the viewer's mood. He's patient, dreamy, and completely unaware that his butterflies have become an unofficial school communication network used for everything from love notes to exam answers.",
     ["Gentle", "Dreamer", "Creative", "Oblivious"],
     [("Butterfly Enthusiasts", "Oscar gives tours of his butterfly greenhouse every Sunday."),
      ("Collaborators", "He's trying to breed a butterfly that can carry spoken messages. It's not going well.")],
     ["Oscar's butterflies seem to know things they shouldn't.", "The administration has been trying to figure out who runs the 'butterfly post' for months."]),

    ("Valentina Rossi (she/her)",
     "Valentina is flamboyant, loud, and absolutely convinced that fashion is a form of magic. She enchants her own clothes — cloaks that billow dramatically regardless of wind, boots that click satisfyingly on every surface, and a scarf that changes colour to match her mood. She's studying Artificing to 'revolutionise the magical fashion industry.' People laugh. She doesn't care.",
     ["Fashionable", "Creative", "Confident", "Eccentric"],
     [("Models", "Valentina needs people to wear her creations. All body types. All species."),
      ("Business Partners", "She's planning to launch a brand after graduation and needs a business mind.")],
     ["Valentina's enchanted dress at the winter ball caused three people to fall in love. With the dress.", "Her family owns a mundane fashion house and has no idea about the magic."]),

    ("Miles Cooper (he/him)",
     "Miles is a mundaneborn who is convinced he's living in a dream. After two years, he still can't quite believe magic is real, which gives him an outsider's perspective that is either refreshingly honest or deeply annoying depending on who you ask. He documents everything in a journal that is part diary, part field notes, part existential crisis.",
     ["Skeptical", "Curious", "Honest", "Nerdy"],
     [("Fellow Mundaneborns", "Miles wants to connect with people who still find all of this absolutely insane."),
      ("Guides", "Someone who can explain the cultural stuff that textbooks don't cover.")],
     ["Miles's journal has been getting thicker at an alarming rate.", "He asked a professor 'but why does magic work?' and reportedly broke them."]),

    ("Noor Al-Bakri (she/her)",
     "Noor is a calligrapher whose script carries magical properties. Her handwritten notes glow faintly, her letters arrive faster than owl post, and she once wrote a ward so beautiful it was framed and hung in the headmistress's office. She's quiet, precise, and deeply invested in the dying art of written magic in a world that's moving toward spoken spells.",
     ["Artistic", "Precise", "Traditional", "Passionate"],
     [("Calligraphy Students", "Noor teaches informal calligraphy workshops. All skill levels welcome."),
      ("Preservation Partners", "She's documenting endangered forms of written magic and needs help.")],
     ["Noor's handwriting is said to be literally impossible to forge.", "She received a mysterious letter written in a script she doesn't recognise but can somehow read."]),

    ("Patrick Byrne (he/him)",
     "Patrick is the funniest person in school and the saddest person in the room. He's the class clown, the life of every party, and completely incapable of having a serious conversation. He uses humour as armour and everyone knows it but nobody wants to be the one to take it away because he's *really* funny. He's studying Curse-Breaking because he likes solving puzzles that aren't himself.",
     ["Funny", "Outgoing", "Deflective", "Sad"],
     [("Comedy Night", "Patrick is organising an open mic. Material can be magical or mundane."),
      ("Someone Real", "He needs a friend who won't let him joke their way out of a real conversation.")],
     ["Patrick hasn't been home for holidays in two years.", "His stand-up routine at the talent show made three people cry laughing. And one person just cry."]),

    ("Selma Hedström (she/her)",
     "Selma is an amateur historian obsessed with the school's past. She's found hidden rooms, decoded old headmasters' journals, and is building a timeline of every significant event in the school's history. She's meticulous, obsessive, and genuinely believes the school is hiding something about its founding. The administration finds her very inconvenient.",
     ["Intellectual", "Obsessive", "Brave", "Stubborn"],
     [("Research Team", "Selma is assembling a team to investigate the school's sealed archives."),
      ("Sceptics", "She actually wants people who'll challenge her theories. The echo chamber is boring.")],
     ["Selma found a room that doesn't appear on any school map.", "The previous school historian graduated under mysterious circumstances."]),

    ("Vincent Park (he/him)",
     "Vincent is a potions prodigy with a terrible bedside manner. He can brew anything — healing draughts, enhancement elixirs, things that technically shouldn't be possible — but he refuses to explain his methods, claiming they're 'intuitive.' He's arrogant, solitary, and secretly generous: the school infirmary's anonymous potion donations all smell like his particular blend of rosemary and spite.",
     ["Prodigy", "Arrogant", "Generous", "Loner"],
     [("Lab Partner", "Vincent doesn't want one. But his professor is making him find one."),
      ("Clients", "Need a custom potion? Vincent might brew it. If you interest him.")],
     ["Vincent's potions consistently outperform commercially available ones.", "He was reportedly offered a job by a pharmaceutical company at age fifteen."]),

    ("Rowan Blake (they/them)",
     "Rowan is a non-binary student who arrived without a backstory and seems determined to keep it that way. They're helpful, present, and completely opaque about anything personal. They know sign language, three dead magical languages, and have a knack for appearing exactly when someone needs help. Some students have started a conspiracy theory that there are multiple Rowans.",
     ["Helpful", "Mysterious", "Multilingual", "Present"],
     [("Language Exchange", "Rowan is offering to teach dead magical languages in exchange for literally any personal information about themselves."),
      ("Mystery Solvers", "Someone figure out where Rowan actually comes from. Please.")],
     ["Rowan has been seen in two places at once on at least three occasions.", "They received no mail for the entire first term."]),

    ("Charlotte Webb (she/her)",
     "Charlotte is a textiles student who weaves magic into fabric. Her tapestries tell stories that change depending on the viewer's emotional state, and her scarves provide genuine warmth — emotional, not just thermal. She's calm, nurturing, and runs a knitting circle that has become the school's unofficial therapy group. Nobody planned this. It just happened.",
     ["Creative", "Nurturing", "Calm", "Wise"],
     [("Knitting Circle", "Thursday evenings. Yarn provided. Crying permitted."),
      ("Collaborators", "Charlotte wants to create an enchanted tapestry for the school. She needs stories.")],
     ["Charlotte's blankets are in such high demand that there's a waiting list.", "She reportedly wove a tapestry that showed someone's future. She burned it."]),

    ("Dante Marchetti (he/him)",
     "Dante is a second-generation immigrant whose family runs a magical apothecary in the city. He grew up surrounded by potions, powders, and customers' problems. He's streetwise in a way that most students aren't, practical in his approach to magic, and deeply unimpressed by theoretical debates. He's here on his family's savings and takes that responsibility seriously.",
     ["Practical", "Streetwise", "Responsible", "Proud"],
     [("Business Contacts", "Dante is always networking. The apothecary needs suppliers and customers."),
      ("Friends", "Actual friends who aren't just trying to get a discount.")],
     ["Dante's family apothecary was fined for selling restricted ingredients. He says they were framed.", "He can identify over 200 ingredients by smell alone."]),

    ("Elise Bjornsson (she/her)",
     "Elise is studying transformation magic — specifically, self-transformation. She can change her hair colour at will, alter her features slightly, and is working toward full shapeshifting. The philosophical implications fascinate her: if you can become anyone, who are you? She's introspective, experimental, and changes her appearance so often that people sometimes don't recognise her.",
     ["Shapeshifter", "Philosophical", "Experimental", "Restless"],
     [("Identity Discussions", "Elise hosts a discussion group about the ethics of transformation magic."),
      ("Study Partners", "She needs someone to document her transformations objectively.")],
     ["Elise once attended a class as someone else. Nobody noticed for an hour.", "She keeps a photo album of every face she's ever worn."]),

    ("Kwame Asante (he/him)",
     "Kwame is a drum maker from a tradition where percussion IS magic. Each drum he builds is attuned to a specific magical frequency. He's frustrated by the school's narrow definition of spellcasting and has been quietly building a case for percussion magic as a legitimate discipline. He's patient, methodical, and his drumming at sunset has become a beloved school tradition.",
     ["Musical", "Traditional", "Patient", "Determined"],
     [("Musicians", "Kwame is forming a percussion ensemble. No experience needed — just rhythm."),
      ("Academic Allies", "Help him get percussion magic recognised as a valid study path.")],
     ["Kwame's drums can be heard from anywhere in the school when he wants them to be.", "A drum he made for a professor reportedly cured their chronic headaches."]),

    ("Hanna Virtanen (she/her)",
     "Hanna is a Finnish student who practices a form of magic rooted in sauna rituals and ice swimming. She's hardy, straightforward, and finds the school overheated in every sense. She speaks rarely but decisively, and her idea of bonding is sitting in silence in a very hot room followed by jumping into a very cold lake. People who survive this process become lifelong friends.",
     ["Stoic", "Tough", "Loyal", "Blunt"],
     [("Sauna Club", "Hanna has built an unofficial sauna behind the gymnasium. You're invited."),
      ("Training Partners", "Cold water immersion, endurance training, and silence. Interested?")],
     ["Hanna swims in the lake every morning. Including winter.", "Her sauna rituals have a higher success rate than some official healing methods."]),

    ("Marcus Lindström (he/him)",
     "Marcus is the school's unofficial therapist — not because he's trained, but because he has the kind of face that makes people tell him things. He sits in the common room, drinks his coffee, and people just... confess. He's kind, overwhelmed, and has accidentally accumulated enough secrets to blackmail the entire school. He would never. Probably.",
     ["Empathetic", "Overwhelmed", "Trustworthy", "Accidental"],
     [("Coffee Companion", "Marcus drinks coffee in the common room every evening. Conversation not required but usually happens."),
      ("Boundaries", "He needs someone to teach him how to say no.")],
     ["Marcus knows who's dating who before the people involved do.", "He reportedly fell asleep during a confession and the person didn't notice."]),

    ("Adriana Costa (she/her)",
     "Adriana is a competitive swimmer who discovered that water magic enhances her athletic performance. She's now torn between a magical education and an Olympic dream. She trains at dawn, studies during the day, and collapses at night. She's disciplined, conflicted, and increasingly aware that she'll have to choose one world eventually.",
     ["Athletic", "Disciplined", "Conflicted", "Competitive"],
     [("Training Partners", "Adriana needs someone to train with at 5am. Non-negotiable time."),
      ("Advice", "Anyone who's straddled the magical and mundane worlds — how do you choose?")],
     ["Adriana holds a mundane regional swimming record that shouldn't be physically possible.", "The sports ministry has started asking questions about her 'technique.'"]),

    ("Niels Bakker (he/him)",
     "Niels is an artificer who builds magical prosthetics. He lost his left hand in an accident as a child and built a replacement that's better than the original. This experience gave him a passion for accessibility in the magical world, which he finds shockingly behind the times. He's creative, angry about injustice, and makes things that work.",
     ["Inventive", "Passionate", "Practical", "Activist"],
     [("Workshop Assistants", "Niels runs a free repair clinic for magical devices. Help needed."),
      ("Accessibility Advocates", "The school needs ramps, magical aids, and someone willing to fight for them.")],
     ["Niels's prosthetic hand can do things a biological hand can't.", "He's been quietly modifying school infrastructure to be more accessible without telling anyone."]),

    ("Vera Sokolov (she/her)",
     "Vera is a dancer who incorporates movement into spellcasting. Her magic looks like choreography — fluid, precise, and beautiful. She's been trying to get dance recognised as a valid casting method, with mixed results. She's graceful, persistent, and has an iron will hidden under layers of silk and sequins.",
     ["Graceful", "Persistent", "Creative", "Underestimated"],
     [("Dance Troupe", "Vera is forming a magical dance company. No dance experience needed — just willingness."),
      ("Supporters", "She needs allies for her proposal to the academic board.")],
     ["Vera's dance-casting is reportedly 30% more efficient than wand-based casting for certain spells.", "She danced a ward into existence during an emergency. Nobody could explain how."]),

    ("Simon Berg (he/him)",
     "Simon is a mundaneborn who made friends with the school's ghosts before he made friends with any living students. He finds dead people less confusing than living ones. He's socially awkward, historically knowledgeable, and has a unique perspective on the school thanks to friends who were there centuries ago. He's slowly learning that living people are worth talking to as well.",
     ["Awkward", "Intellectual", "Friendly", "Unconventional"],
     [("History Buffs", "Simon has access to firsthand accounts of school history. Via ghosts."),
      ("Social Skills", "He needs patient people who can teach him small talk.")],
     ["Simon's ghost friends are reportedly jealous of his living friendships.", "He knows the location of rooms that were walled up centuries ago."]),

    ("Olivia Strand (she/her)",
     "Olivia is a hexborn who rejected her family's expectations so thoroughly that she's studying mundane science alongside magic. She believes the two disciplines are describing the same phenomena in different languages and is working on a unified theory. She's intense, stubborn, and will talk your ear off about quantum entanglement and sympathetic magic being the same thing.",
     ["Scientific", "Rebellious", "Intellectual", "Intense"],
     [("Cross-disciplinary Researchers", "Olivia needs people who speak both science and magic."),
      ("Debate Partners", "Challenge her unified theory. She wants to stress-test it.")],
     ["Olivia has a secret laboratory where she runs experiments that combine magic and physics.", "Her family has cut her allowance over her 'mundane obsession.'"]),

    ("Tobias Engel (he/him)",
     "Tobias is a certified disaster who is somehow beloved by everyone. He trips over his own feet, mispronounces spells in hilarious ways, and once accidentally turned his own hair into spaghetti for a week. But he's so genuine, so kind, and so eager to help that people can't help but root for him. He's improving — slowly — and his determination is quietly inspiring.",
     ["Clumsy", "Kind", "Determined", "Lovable"],
     [("Patient Mentors", "Tobias needs someone who won't lose their mind when he turns their textbook into a frog. Again."),
      ("Friends", "He'll be your most enthusiastic supporter in anything you do.")],
     ["Tobias once accidentally cast a spell perfectly while trying to cast a completely different spell.", "His magical mishaps have accidentally solved two separate school problems."]),

    ("Helena Antonescu (she/her)",
     "Helena is a Romanian student from a long line of vampire hunters who is now, awkwardly, best friends with a vampire's descendant. She's fierce, superstitious, and carries more garlic than any reasonable person should. She's studying Guardian path with a specialty in dark creature defence, though her definition of 'dark creature' has been evolving rapidly thanks to her unlikely friendship.",
     ["Fierce", "Superstitious", "Loyal", "Evolving"],
     [("Defence Study Group", "Helena's group focuses on practical protection magic. No theoretical fluff."),
      ("Unlikely Friends", "She's learning that the world isn't as black and white as her family taught her.")],
     ["Helena's crossbow is enchanted and technically shouldn't be on school grounds.", "Her family sent her here to recruit. She's having second thoughts."]),

    ("Dennis Kuznetsov (he/him)",
     "Dennis is a chess grandmaster who applies game theory to everything. He sees the school as a complex system of moves and counter-moves, and he's always three steps ahead — or at least he thinks he is. He's brilliant, insufferable, and oddly charming when he forgets to be strategic. He plays speed chess in the cafeteria and narrates his thought process whether you asked or not.",
     ["Strategic", "Intellectual", "Competitive", "Insufferable"],
     [("Chess", "Dennis needs opponents. He'll play anyone, anywhere, anytime."),
      ("Strategists", "He's forming a war games club. The school doesn't know yet.")],
     ["Dennis reportedly predicted the outcome of a duel by analysing both fighters' historical patterns.", "He's been secretly teaching strategy to the fireball dragon team."]),

    ("Lila Fernandez (she/her)",
     "Lila is a lucid dreamer who can enter and navigate the dreamscape — a shared magical dreamspace that most people only access unconsciously. She's been mapping it since she was twelve and has found things there that concern her. She's ethereal, distracted, and sometimes it's hard to tell if she's fully awake. She sleeps a lot. People think she's lazy. She's working.",
     ["Dreamer", "Mysterious", "Distracted", "Brave"],
     [("Dream Explorers", "Lila can teach you to lucid dream if you're willing to face what's in there."),
      ("Research Partners", "Something in the dreamscape is changing and she needs help documenting it.")],
     ["Lila has spent more time in the dreamscape than some people have spent awake.", "She once woke up with an object she found in a dream. It shouldn't be possible."]),

    ("Arthur Delacroix (he/him)",
     "Arthur is a French exchange student who carries himself like a 19th-century dandy and speaks with the vocabulary of one. He's an excellent duellist, a mediocre student, and a surprisingly good listener. He's here for one year and seems determined to make it memorable. He writes long, flowery letters home and receives exactly none back.",
     ["Romantic", "Old-fashioned", "Skilled", "Lonely"],
     [("Duelling", "Arthur is always ready for a formal duel. Etiquette strictly observed."),
      ("Correspondence", "He wants a pen pal. The art of letter writing is dying and he takes it personally.")],
     ["Arthur's family didn't send him here voluntarily. Or so the rumours say.", "He once wrote a poem so moving that the parchment wept."]),

    ("Naomi Ito (she/her)",
     "Naomi is a photographer whose magical camera captures things invisible to the naked eye — auras, emotional residue, magical traces. She documents the school obsessively and has built an archive that's part art project, part surveillance network. She's observant, ethical about consent (she always asks), and producing work that is genuinely beautiful and occasionally accidentally evidence.",
     ["Artistic", "Observant", "Ethical", "Meticulous"],
     [("Photography Subjects", "Naomi is working on a portrait series. She wants to photograph every student."),
      ("Exhibition Help", "She's planning a gallery show and needs someone to help curate.")],
     ["Naomi's photos have revealed magical residue in places the school claims are warded clean.", "Her camera once captured an image of someone who wasn't in the room."]),

    ("Gustav Ek (he/him)",
     "Gustav is the son of the school's previous groundskeeper and grew up on campus. He knows the building better than the headmistress — every shortcut, every hidden passage, every room that 'doesn't exist.' He's quiet, territorial, and considers the school his home in a way no student or teacher can match. He's studying here now because it felt wrong to be anywhere else.",
     ["Quiet", "Knowledgeable", "Protective", "Territorial"],
     [("Tours", "Gustav can show you parts of the school you didn't know existed. If he trusts you."),
      ("Preservation", "He wants to document the school's physical history before renovations destroy it.")],
     ["Gustav has keys to doors that even the administration has forgotten.", "He was born in the school. Literally — in the infirmary during a snowstorm."]),

    ("Diana Popescu (she/her)",
     "Diana is a mundaneborn who compensates for her late start with sheer force of will and an extensive spreadsheet system. She has optimised her study schedule down to 15-minute intervals and has a five-year plan that accounts for three contingencies. She's type-A, anxious, and would be insufferable if she weren't so genuinely helpful to everyone around her.",
     ["Organised", "Anxious", "Helpful", "Hardworking"],
     [("Study System", "Diana has developed a study method that she swears works. Free workshops available."),
      ("Relaxation Teachers", "She needs someone to teach her how to take a break. Seriously. Help.")],
     ["Diana's spreadsheets are rumoured to be magically enhanced for efficiency.", "She once scheduled a 'spontaneous fun' block in her calendar. It didn't work."]),

    ("Hassan Khalil (he/him)",
     "Hassan is the kind of student who asks 'but why?' until the professor runs out of answers. He's not being difficult — he genuinely, desperately needs to understand why magic works the way it does, at a fundamental level. He's brilliant, obsessive, and increasingly isolated as his questions get weirder and his research gets darker. Not dark as in evil — dark as in 'staring into the abyss of magical theory.'",
     ["Obsessive", "Intellectual", "Brilliant", "Isolated"],
     [("Theoretical Magic Enthusiasts", "Hassan has a discussion group about the fundamental nature of magic. It meets at weird hours."),
      ("Someone Normal", "He needs a friend who'll drag him to lunch and make him talk about something else.")],
     ["Hassan asked a question in class that the professor couldn't answer. The professor left the room.", "His research notes are in a cipher that nobody else can read."]),

    ("Astrid Johansson (she/her)",
     "Astrid is a blacksmith — a genuine, forge-and-anvil blacksmith who makes magical weapons and tools. She's covered in burn scars she wears proudly, speaks bluntly, and has no patience for people who think artificing is just 'enchanting things.' She makes things from scratch: mines the ore, smelts the metal, shapes the blade, weaves the magic in. She's the real deal and she knows it.",
     ["Craftsperson", "Blunt", "Proud", "Skilled"],
     [("Apprentices", "Astrid will teach you to forge if you can handle the heat. And the criticism."),
      ("Commissions", "Custom magical tools, weapons, and jewellery. Not cheap. Worth it.")],
     ["Astrid's forge burns hotter than it should be physically possible.", "She once made a knife for a professor that was so good they reportedly cried."]),

    ("Roberto Fiore (he/him)",
     "Roberto is an Italian exchange student who discovered that his family's traditional cooking magic is considered 'primitive' by mainstream magical academia. He's here to prove them wrong. He's passionate about food, family, and cultural preservation. He cooks massive meals for anyone who'll eat them and takes it personally when people skip breakfast.",
     ["Passionate", "Traditional", "Generous", "Sensitive"],
     [("Dinner Companions", "Roberto cooks. You eat. It's simple. Every Thursday."),
      ("Cultural Exchange", "He wants to learn about everyone's food traditions.")],
     ["Roberto's cooking once cured a student's cold. The school nurse was confused.", "His nonna's recipes are written in a magical dialect that linguists are interested in."]),

    ("Saga Nilsson (she/her)",
     "Saga reads tarot — but not the way most diviners do. She treats the cards as a therapeutic tool, not a predictive one. She helps people understand themselves, not their future. She's become the school's unofficial counsellor for students who don't trust the official one. She's wise beyond her years, emotionally mature, and only 17, which she finds both empowering and terrifying.",
     ["Wise", "Empathetic", "Mature", "Young"],
     [("Tarot Readings", "Saga does readings by appointment. For self-understanding, not fortune-telling."),
      ("Peer Counsellors", "She wants to train other students in therapeutic tarot techniques.")],
     ["Students who visit Saga report feeling better without being able to explain why.", "The school counsellor has been suspiciously supportive of Saga's work."]),

    ("Thibault Moreau (he/him)",
     "Thibault is a prefect who takes the role far too seriously. He patrols corridors with a clipboard, enforces quiet hours with gentle disappointment, and has memorised the student handbook cover to cover. He's insufferable and irreplaceable. When things go wrong — and they always go wrong — Thibault is the one who knows exactly which protocol applies.",
     ["Rule-follower", "Responsible", "Insufferable", "Reliable"],
     [("Prefect Team", "Thibault is recruiting responsible students for corridor duty."),
      ("Rule Breakers", "He's willing to negotiate. But you have to ask nicely.")],
     ["Thibault once cited a rule that even the headmistress had forgotten existed.", "He cried when he had to issue his first official warning."]),

    ("Marina Volkov (she/her)",
     "Marina is a competitive athlete who discovered that enhancement magic exists and now has complicated feelings about everything she's ever achieved. Was her talent natural? Was she subconsciously using magic all along? She's in an existential crisis disguised as a sports career. She's fast, strong, and profoundly uncertain about everything.",
     ["Athletic", "Conflicted", "Competitive", "Introspective"],
     [("Athletes", "Marina wants to meet other student athletes who are navigating the magic/mundane sports divide."),
      ("Philosophers", "Someone help her figure out what 'fair competition' means when magic exists.")],
     ["Marina has broken athletic records that shouldn't be possible without magical assistance.", "She's been testing herself for magical enhancement and the results are inconclusive."]),

    ("Philip Larsen (he/him)",
     "Philip writes code. In a school of magic. He's a mundaneborn who believes programming and spellcasting share the same underlying logic and is attempting to create a magical programming language. Most people think he's wasting his time. He's actually onto something, but he needs magical expertise he doesn't have. He's intense, sleep-deprived, and runs on energy drinks and conviction.",
     ["Nerdy", "Innovative", "Intense", "Sleep-deprived"],
     [("Magical Programmers", "Philip needs people who understand both code and spellwork."),
      ("Testers", "His prototype needs testing. Side effects may include mild temporal displacement.")],
     ["Philip's program successfully cast a spell last week. It was the wrong spell, but still.", "The Arithmancy professor has been quietly monitoring his work."]),

    ("Elke Janssen (she/her)",
     "Elke is a twins researcher — specifically, she's studying the magical bond between twins after her own twin sister chose not to attend a magical school. She feels half of herself is missing and has channelled that into academic obsession. She's brilliant, lonely, and writes letters to her sister that get longer every week.",
     ["Intellectual", "Lonely", "Dedicated", "Sensitive"],
     [("Twins", "Elke wants to interview anyone who has a twin, magical or otherwise."),
      ("Friends", "She needs people who'll be physically present. She's had enough of long-distance relationships.")],
     ["Elke can reportedly sense her twin's emotions from hundreds of miles away.", "Her research has attracted attention from the Ministry's Department of Magical Bonds."]),

    ("Adam Nowak (he/him)",
     "Adam is a quiet kid who found his voice through debate club and now won't shut up. He's gone from 'too shy to order coffee' to 'will argue with a professor about the ethical implications of transmutation' in eighteen months. The transformation is remarkable, if occasionally exhausting. He's growing into himself in real time and it's messy and beautiful.",
     ["Eloquent", "Growing", "Passionate", "Awkward"],
     [("Debate Club", "Adam runs weekly debates. All topics. All skill levels. Passion more important than polish."),
      ("Mentees", "He wants to help other shy students find their voices.")],
     ["Adam won the inter-school debate championship as a first-year. Nobody expected it, including Adam.", "His debate notes are filled with doodles of what look like architectural plans."]),

    ("Cynthia Okafor (she/her)",
     "Cynthia is the school's best potioneer and she knows it. She's graceful under pressure, innovative in her approach, and handles volatile ingredients with a surgeon's precision. She's competitive but fair, and she mentors younger students with a patience that surprises people. She wants to develop potions that make healing accessible to non-magical communities.",
     ["Skilled", "Ambitious", "Graceful", "Mentoring"],
     [("Lab Partners", "Cynthia is working on a project that requires multiple brewers working in sync."),
      ("Outreach", "She wants to discuss the ethics of sharing magical remedies with mundane communities.")],
     ["Cynthia developed a variant of a standard potion that's 40% more effective.", "A pharmaceutical company has already approached her about a post-graduation position."]),

    ("Jakob Winter (he/him)",
     "Jakob collects magical artifacts the way some people collect stamps. His dorm room is a museum of curiosities, half of which are probably cursed. He swears he's tested them all. He hasn't. He's cheerful, reckless, and has an encyclopedic knowledge of magical objects that makes him useful in exactly the kinds of situations you shouldn't be in.",
     ["Collector", "Reckless", "Knowledgeable", "Cheerful"],
     [("Fellow Collectors", "Jakob wants to meet other people who appreciate magical objects."),
      ("Curse-Breakers", "He has a few items he can't quite figure out. Professional help would be nice.")],
     ["At least one of Jakob's artifacts is an unregistered magical weapon.", "He found something in the school's lost and found that the school claims was never there."]),

    ("Mia Bergström (she/her)",
     "Mia is a weather witch who can sense atmospheric changes before any instrument. She predicts storms, snow days, and once, memorably, a magical weather event that wasn't on any forecast. She's calm, grounded, and has a presence that makes rooms feel quieter. She speaks slowly and people have learned to listen, because when Mia says something is coming, it's coming.",
     ["Intuitive", "Calm", "Respected", "Patient"],
     [("Weather Enthusiasts", "Mia gives daily weather briefings in the common room. They're weirdly popular."),
      ("Emergency Team", "She wants to form a student weather response team for magical storms.")],
     ["Mia predicted a magical storm that meteorological instruments missed entirely.", "She can reportedly calm minor weather patterns by concentrating."]),

    ("Leo Baumann (he/him)",
     "Leo builds clocks. Magical clocks, mundane clocks, clocks that tell time, clocks that tell emotions, and one clock that he claims tells the truth (it's always pointing at 'it's complicated'). He's a detail-oriented artificer who finds the passage of time philosophically fascinating. He's punctual, precise, and will notice if you're three minutes late.",
     ["Precise", "Philosophical", "Creative", "Punctual"],
     [("Apprentices", "Leo teaches clockwork artificing in his workshop. Steady hands required."),
      ("Philosophers", "He hosts discussions about the nature of time. Refreshments provided.")],
     ["Leo's truth-telling clock has been getting more specific lately.", "He built a clock that ran backwards for a week. Nobody is sure what happened during that week."]),

    ("Ruth Goldstein (she/her)",
     "Ruth is a mundaneborn who enrolled at age 25 after a career in mundane law. She's the oldest student in her year and handles this with a maturity that makes younger students either rely on her or resent her. She's studying magical law because she believes the wizarding legal system is 'a century behind mundane jurisprudence' and she intends to fix it.",
     ["Mature", "Ambitious", "Blunt", "Experienced"],
     [("Legal Eagles", "Ruth is starting a magical law study group. Justice shouldn't require a trust fund."),
      ("Mentees", "She's happy to advise younger students on life, career, and the art of not panicking.")],
     ["Ruth has already identified seventeen legal precedents she wants to challenge.", "The administration is reportedly nervous about having a trained lawyer as a student."]),

    ("Connor Walsh (he/him)",
     "Connor is a sports journalist who covers the school's duelling and fireball dragon scenes with the intensity of a war correspondent. He produces a weekly podcast, writes match analyses, and has sources in every team. He's energetic, nosy, and genuinely believes sports journalism is a calling. He's also a decent duellist himself but prefers watching to competing.",
     ["Journalist", "Energetic", "Knowledgeable", "Nosy"],
     [("Sources", "Connor needs inside information from every sports team. Anonymity guaranteed."),
      ("Co-hosts", "The podcast needs a commentator with personality.")],
     ["Connor's match predictions are right more often than the official bookmaker.", "He has audio recordings that certain people would prefer didn't exist."]),

    ("Irina Kozlov (she/her)",
     "Irina is a dancer and duellist who combines both disciplines into something terrifyingly beautiful. She fights like she's performing and performs like she's fighting. She's Russian-born, impeccably disciplined, and has a competitive streak that borders on pathological. She respects only strength and skill, which makes her difficult to befriend but extraordinary to watch.",
     ["Disciplined", "Competitive", "Graceful", "Intimidating"],
     [("Worthy Opponents", "Irina wants to duel the best. She's not interested in easy wins."),
      ("Dance Partners", "She's choreographing a piece that combines dance and combat magic.")],
     ["Irina's duelling record is undefeated in her previous school.", "She trains for four hours every morning and considers this light exercise."]),

    ("Thomas Eriksen (he/him)",
     "Thomas is the school's amateur archaeologist who spends weekends digging holes in the school grounds and finding things that range from 'interesting' to 'probably should have stayed buried.' He's enthusiastic, muddy, and keeps a detailed log of every artefact he's found. The groundskeeper hates him. The history professor loves him.",
     ["Adventurous", "Enthusiastic", "Dirty", "Academic"],
     [("Dig Team", "Thomas needs help with a new excavation site he's found behind the greenhouse."),
      ("Cataloguers", "The artefacts need proper documentation. Detail-oriented volunteers needed.")],
     ["Thomas found something last month that made the history professor go very quiet.", "His excavations have accidentally uncovered structural weaknesses in the school's foundations."]),

    ("Annika Stein (she/her)",
     "Annika is a hexborn who has been raised to believe she's destined for greatness. The problem is, she's perfectly average. She's dealing with this realisation with the grace of someone whose entire identity is collapsing. She's snippy, defensive, and slowly discovering that being ordinary might actually be okay — a revolutionary thought in her family.",
     ["Defensive", "Growing", "Honest", "Vulnerable"],
     [("Support", "Annika is learning to be okay with being okay. Fellow recovering overachievers welcome."),
      ("Friends", "People who like her for who she is, not who her family says she should be.")],
     ["Annika's family has been planning her career since before she was born.", "She secretly volunteers at the school kitchen because cooking is the only thing she chose for herself."]),

    ("Omar Farouk (he/him)",
     "Omar is a medical student on the Healer path who wants to specialise in magical diseases — conditions that only affect wizards and have no mundane equivalent. He's seen suffering that most students don't know exists and carries it with quiet intensity. He's studious, empathetic, and has no patience for people who treat healing as a backup career for those who can't duel.",
     ["Dedicated", "Empathetic", "Serious", "Passionate"],
     [("Healer Students", "Omar runs case study discussions for aspiring healers."),
      ("Volunteers", "The school clinic needs more volunteer hours. People need help.")],
     ["Omar has treated conditions that aren't in any textbook.", "He exchanges letters with healers in three different countries about unsolved cases."]),

    ("Katarina Novak (she/her)",
     "Katarina is a mathematical genius who sees magic as applied mathematics. She can calculate spell trajectories in her head, optimise ward configurations for maximum efficiency, and has an unsettling habit of quantifying things that shouldn't be quantifiable (she once rated a sunset at 7.3 out of 10). She's awkward, brilliant, and trying to understand why people don't find numbers as comforting as she does.",
     ["Mathematical", "Awkward", "Brilliant", "Analytical"],
     [("Math Nerds", "Katarina hosts a 'Mathematical Magic' seminar. It's exactly as intense as it sounds."),
      ("Normal People", "She needs friends who can explain jokes to her. She's working on humour.")],
     ["Katarina solved a ward equation that had stumped the faculty for a decade.", "She rates social interactions on a spreadsheet and is apparently improving."]),

    ("Julian Priest (he/him)",
     "Julian is the child of two school administrators who he is absolutely nothing like. Where they are strict and structured, he is chaotic and creative. He makes enchanted fireworks, builds magical prank devices, and has been given more detentions than anyone in recent memory. He's not malicious — he's bored, brilliant, and channelling his energy in the only direction that feels real.",
     ["Chaotic", "Creative", "Rebellious", "Brilliant"],
     [("Mayhem", "Julian is planning something spectacular. Plausible deniability available."),
      ("Mentors", "Someone needs to help him channel this energy before he blows something up. Again.")],
     ["Julian's parents have offered rewards for anyone who can get him to behave.", "His 'accidental' fireworks display at the opening ceremony was actually quite beautiful."]),

    ("Alma Hedberg (she/her)",
     "Alma is a beekeeper. Her bees are magical, intelligent, and produce honey that has mild healing properties. She's quiet, patient, and speaks to her bees in a low hum that calms everyone in earshot. She's studying Herbology and Creature Care simultaneously and sees no distinction between them. Her honey is the unofficial currency of favours among students who've tasted it.",
     ["Patient", "Nurturing", "Quiet", "Skilled"],
     [("Beekeeping Apprentices", "Alma will teach you about magical bees if you're not allergic. And calm."),
      ("Honey Distribution", "She needs help managing the increasing demand for her honey.")],
     ["Alma's bees are rumoured to be able to find anyone on the school grounds.", "Her honey was once served at a faculty dinner and nobody knew it wasn't from the kitchen."]),

    ("Felix Nowak (he/him)",
     "Felix is an identical twin whose brother attends a different magical school. They can communicate telepathically across any distance, which Felix finds both useful and deeply annoying. He's sociable, slightly chaotic, and often mid-conversation with his brother while appearing to talk to you. He's studying communication magic for obvious reasons.",
     ["Telepathic", "Sociable", "Chaotic", "Distracted"],
     [("Communications Research", "Felix wants to study magical communication methods. He's a living case study."),
      ("Friends", "People who don't mind that he's technically always in two conversations at once.")],
     ["Felix sometimes finishes sentences that his brother started in a different country.", "The Ministry has expressed interest in studying the twins' telepathic bond. They declined."]),

    ("Beatrice von Hardt (she/her)",
     "Beatrice comes from magical nobility and is desperately trying to escape the expectations that come with it. She was raised to be a socialite and diplomat but wants to be a researcher. She's polite, subversive, and uses her perfect manners as a weapon. She'll smile sweetly while dismantling your argument and you'll thank her for it.",
     ["Polite", "Subversive", "Intellectual", "Trapped"],
     [("Research Partners", "Beatrice is conducting fieldwork that her family would not approve of."),
      ("Fellow Escapees", "Other students from restrictive families who are finding their own path.")],
     ["Beatrice's family doesn't know she's changed her academic focus.", "She sent back her debutante dress with a research paper pinned to it."]),

    ("Dorian Frost (he/him)",
     "Dorian is an empath who feels other people's emotions as his own. In a crowded room, he's drowning. He's developed elaborate coping mechanisms — noise-cancelling headphones (for emotions), meditation, long walks alone — but it's getting harder as his power grows. He's sweet, fragile, and the best friend you'll ever have, because he literally feels your pain.",
     ["Empathetic", "Fragile", "Kind", "Overwhelmed"],
     [("Quiet People", "Dorian needs friends who don't feel too loudly."),
      ("Shielding Practice", "He's learning to block emotions and needs patient practice partners.")],
     ["Dorian can tell when someone is lying from across a room.", "He passed out at last year's Fireball Dragon final from emotional overload."]),

    ("Saskia Brouwer (she/her)",
     "Saskia is a gardener, a brewer, and an aspiring poisoner — wait, no, an aspiring toxicologist. She's fascinated by dangerous plants and their applications, which makes her greenhouse the most interesting and most terrifying place in school. She's cheerful, thorough, and labels everything very carefully, which is exactly the kind of person you want working with deadly nightshade.",
     ["Meticulous", "Cheerful", "Dangerous", "Scholarly"],
     [("Herbology Enthusiasts", "Saskia's greenhouse tours are informative. Also, don't touch anything."),
      ("Research Partners", "She's studying the medicinal applications of magical toxins. Serious inquiries only.")],
     ["Saskia's greenhouse contains at least three plants that are technically illegal.", "She once accidentally poisoned the entire herbology class. Everyone survived, but barely."]),

    ("Lars Pedersen (he/him)",
     "Lars is a lighthouse keeper's son who grew up isolated on a tiny island. He's adjusting to school life with the bewilderment of someone who spent his childhood talking to seagulls. He's quiet, overwhelmed by crowds, and has a working knowledge of maritime magic that nobody else in school possesses. He misses the sea so much it's almost physical.",
     ["Quiet", "Homesick", "Knowledgeable", "Gentle"],
     [("Nature Lovers", "Lars needs to spend time outdoors with people who appreciate silence."),
      ("Maritime Magic", "He can teach you things about water and weather that aren't in any textbook.")],
     ["Lars's lighthouse supposedly guides more than just ships.", "He can predict weather changes by watching the behaviour of birds."]),

    ("Margot Dubois (she/her)",
     "Margot is a perfumer who creates magical scents. Each one triggers specific emotional states: nostalgia, courage, calm, joy. She treats fragrance as a form of emotional magic and considers herself a healer, though the Healer department disagrees. She's sophisticated, persuasive, and her room smells like a different emotion every day.",
     ["Creative", "Sophisticated", "Persuasive", "Unconventional"],
     [("Test Subjects", "Margot needs people to test new fragrances. Side effects are mostly pleasant."),
      ("Healer Allies", "Help her convince the Healer department that aromatherapy is real magic.")],
     ["Students who visit Margot's room report feeling inexplicably happy afterwards.", "A perfume she created for the headmistress is reportedly the school's most effective calming tool."]),

    ("Ernst Weber (he/him)",
     "Ernst is a taxidermist. Of magical creatures. It's an ancient and respected craft in certain circles and deeply unsettling in all other circles. He preserves specimens for the school's museum, the library, and his own collection (which is extensive and not entirely approved). He's meticulous, passionate, and genuinely doesn't understand why people find his hobby disturbing.",
     ["Meticulous", "Passionate", "Eccentric", "Oblivious"],
     [("Museum Volunteers", "The school's natural history collection needs curators."),
      ("Creature Studies", "Ernst's collection is available for academic study. Just don't call them 'creepy.'")],
     ["Ernst's collection includes a specimen that officially doesn't exist.", "He once brought a project to dinner. The table cleared in thirty seconds."]),

    ("Alina Popa (she/her)",
     "Alina is a memory mage — she can revisit her own memories with perfect clarity and has been developing techniques to help others do the same. It started as a study technique (why read a textbook twice when you can just remember it perfectly?) and evolved into something more profound. She helps students recover lost memories, process trauma, and study for exams. The therapeutic applications fascinate her.",
     ["Intellectual", "Empathetic", "Gifted", "Careful"],
     [("Memory Workshops", "Alina teaches memory enhancement techniques. Useful for exams and for life."),
      ("Therapy Research", "She's exploring memory magic as a therapeutic tool and needs case studies.")],
     ["Alina once helped a student recover a memory that changed their understanding of their own life.", "She can't forget anything, even when she wants to. She considers this a curse."]),

    ("Henrik Mikkelsen (he/him)",
     "Henrik is a second-year who spent his first year in the infirmary with a magical illness that no one could diagnose. He's back now, supposedly cured, though he won't talk about what happened or what cured him. He's quiet, watchful, and has a new seriousness that his first-year friends find unsettling. He draws runes in the margins of all his notes.",
     ["Changed", "Quiet", "Serious", "Mysterious"],
     [("Friends", "Henrik wants to reconnect with people who knew him before. He's not the same, but he's trying."),
      ("Healers", "He's studying his own condition and needs friends with medical knowledge.")],
     ["The infirmary staff won't discuss Henrik's case.", "The runes he draws aren't from any known system."]),

    ("Sophie Blanc (she/her)",
     "Sophie is an enthusiastic first-year who treats every single thing about magical school with the wide-eyed wonder of someone who still can't believe this is real. She asks questions that professors find either delightful or exasperating, takes notes in four colours, and has already joined six clubs. Her energy is limitless and her organisation is nonexistent.",
     ["Enthusiastic", "Curious", "Chaotic", "Joyful"],
     [("Everything", "Sophie wants to do EVERYTHING. All clubs. All activities. All friendships."),
      ("Organisers", "She needs someone who can help her manage her schedule before she collapses.")],
     ["Sophie accidentally signed up for the same club twice under different names.", "Her enthusiasm is reportedly so powerful it's mildly contagious."]),

    ("Romain Leclerc (he/him)",
     "Romain is a sommelier of magical potions — he can taste a potion and tell you every ingredient, its provenance, and whether the brewer was having a bad day. He comes from a family of mundane vintners and sees magical brewing as an extension of the family trade. He's sophisticated, particular, and running an underground potion-tasting club that is technically against twelve school rules.",
     ["Sophisticated", "Perceptive", "Rebellious", "Particular"],
     [("Tasting Club", "Romain's potion appreciation society meets biweekly. Refined palates preferred but not required."),
      ("Brewers", "He wants to collaborate with talented potionmakers on experimental blends.")],
     ["Romain once identified a mislabelled potion that the school nurse had overlooked.", "His tasting notes are so detailed they could serve as brewing instructions."]),

    ("Yara Mansour (she/her)",
     "Yara is a calligrapher turned ward-writer who discovered she could draw protective barriers with nothing but ink and intent. Her wards are works of art — literally — and the school has commissioned her to reinforce several classrooms. She's quiet, focused, and deeply proud of a craft that most students don't even know exists.",
     ["Artistic", "Focused", "Proud", "Skilled"],
     [("Apprentices", "Yara is looking for students interested in learning ward-writing. Steady hands required."),
      ("Collectors", "She sells decorative wards. They're beautiful and functional.")],
     ["Yara's wards are rumoured to be stronger than machine-made ones.", "She drew a ward that repelled a professor. Nobody is sure how."]),

    ("Piotr Zielinski (he/him)",
     "Piotr is a sleepwalking spellcaster — he casts complex magic in his sleep and wakes up to discover the results. His roommate has learned to duck. He's studying this condition with a mix of academic curiosity and genuine terror, because the spells are getting more powerful and he has no control over them. He's cheerful during the day and a menace at night.",
     ["Cheerful", "Unpredictable", "Nerdy", "Anxious"],
     [("Sleep Researchers", "Piotr needs someone studying sleep magic or unconscious casting."),
      ("Roommate", "His current roommate is transferring rooms. Anyone brave enough?")],
     ["Piotr's sleep-spells have been getting more complex each month.", "He once sleepwalked to the library, checked out a book, and returned it — all while asleep."]),

    ("Maeve Callaghan (she/her)",
     "Maeve is an Irish student who practices a form of hedge magic passed down through her family for centuries. She makes charms from found objects — feathers, stones, bits of wire — that actually work. The academic establishment considers this 'folk magic' beneath serious study. Maeve considers the academic establishment full of snobs.",
     ["Traditional", "Rebellious", "Creative", "Proud"],
     [("Folk Magic Circle", "Maeve teaches traditional charm-making to anyone interested."),
      ("Allies", "She's campaigning for folk magic to be recognised in the curriculum.")],
     ["Maeve's charms have been confiscated and returned so many times the office has a dedicated drawer.", "A charm she made for a sick student worked better than the prescribed potion."]),

    ("Axel Lindqvist (he/him)",
     "Axel is Theo's younger brother and handles this by being as different as possible. Where Theo is bookish and mysterious, Axel is loud, sporty, and aggressively transparent. He's in the Fireball Dragon Club, the Duelling Club, and has opinions he shares at volume. He loves his sibling fiercely and will fight anyone who bothers them, which Theo finds mortifying.",
     ["Loud", "Athletic", "Protective", "Loyal"],
     [("Teams", "Axel is on every sports team and wants you on one too."),
      ("Siblings", "Other students navigating complicated sibling dynamics at school.")],
     ["Axel once carried Theo out of the library at midnight because they forgot to sleep.", "He challenges someone to a duel at least once a week. His record is mixed."]),

    ("Cleo Papadimitriou (she/her)",
     "Cleo is an astral projector who can separate her consciousness from her body and travel the school unseen. She discovered this ability accidentally during a particularly boring lecture and has been refining it since. She uses it for exploration, not spying (she insists), and has mapped rooms and passages that physical access can't reach. She's secretive about the full extent of her ability.",
     ["Mysterious", "Adventurous", "Secretive", "Gifted"],
     [("Explorers", "Cleo has found places in the school that shouldn't exist. She needs physical help reaching them."),
      ("Researchers", "She wants to understand the theory behind astral projection.")],
     ["Cleo has visited the sealed wing of the school that's been closed for decades.", "She once appeared as a 'ghost' in the first-year dormitory. It was not appreciated."]),

    ("Matteo Bianchi (he/him)",
     "Matteo is a glassblower who creates magical instruments — lenses that reveal hidden things, orbs that store memories, bottles that preserve emotions. His workshop is beautiful and dangerous, full of molten glass and flickering enchantments. He's patient, meticulous, and covered in small burn scars he considers badges of honour.",
     ["Craftsperson", "Patient", "Artistic", "Dedicated"],
     [("Commissions", "Matteo makes custom magical glass instruments. The waiting list is long."),
      ("Workshop Visitors", "He's happy to demonstrate glassblowing to curious students.")],
     ["Matteo created a glass orb that shows different scenes to different viewers.", "His masterwork — a glass violin that plays itself — shattered and he hasn't spoken about it since."]),

    ("Frida Holmberg (she/her)",
     "Frida is a competitive debater who argues for sport and then agonises about whether she was too harsh. She's passionate about magical ethics — specifically, the question of whether magic creates obligations. If you can heal, must you heal? If you can see the future, must you share it? She writes papers that professors find uncomfortable.",
     ["Passionate", "Ethical", "Intellectual", "Anxious"],
     [("Ethics Club", "Frida runs a weekly ethics discussion. Topics are always uncomfortable. That's the point."),
      ("Debate Partners", "She needs opponents who argue in good faith.")],
     ["Frida's ethics paper on the 'obligation of ability' was circulated among faculty without her knowledge.", "She once made a professor cry during a debate. She also cried."]),

    ("Olu Adebayo (he/him)",
     "Olu is a drummer and storyteller from a tradition where the two are inseparable. His stories are performances — complete with rhythmic accompaniment, magical sound effects, and audience participation. He holds court in the common room on Friday nights and has become essential to the school's social fabric. He's generous, charismatic, and more observant than he lets on.",
     ["Charismatic", "Musical", "Storyteller", "Generous"],
     [("Story Night", "Friday evenings. Olu tells stories. You listen. It's magical. Literally."),
      ("Contributors", "He wants to collect and tell other people's stories. Share yours.")],
     ["Olu's stories have been known to cause listeners to experience the events described.", "He's been offered a position at a magical theatre company but hasn't decided yet."]),

    ("Klara Svensson (she/her)",
     "Klara is a twin whose sister is a mundane. She carries enormous guilt about being the 'special' one and overcompensates by downplaying her abilities and sending most of her allowance home. She's kind, self-deprecating, and tries so hard to be ordinary that people sometimes forget she's one of the most talented students in her year.",
     ["Humble", "Kind", "Talented", "Guilty"],
     [("Twin Talk", "Klara wants to meet other students with mundane siblings. The dynamic is... complicated."),
      ("Friends", "People who'll let her be talented without making it weird.")],
     ["Klara's sister doesn't know the extent of her magical abilities.", "She scored highest in her entrance year but asked the school not to announce it."]),

    ("Hamza El-Amin (he/him)",
     "Hamza is a builder. He thinks in structures — arches, buttresses, load-bearing walls. He wants to build magical buildings that are alive, responsive, and beautiful. He spends his free time sketching impossible architecture and has submitted three proposals to renovate the school. All were rejected. He's resubmitting with better drawings.",
     ["Creative", "Determined", "Visionary", "Stubborn"],
     [("Architects", "Hamza needs people who dream about buildings."),
      ("Engineers", "His designs need structural analysis from someone more practical than him.")],
     ["Hamza's sketches include a building that exists in two places simultaneously.", "He found a structural flaw in the school that the maintenance team hadn't noticed."]),

    ("Nathalie Girard (she/her)",
     "Nathalie is a mundaneborn who arrived at school with a chemistry degree and a bone to pick with magical education. She thinks potions class is 'just chemistry with worse safety protocols' and has been campaigning for modernised lab equipment. She's right about the safety protocols, which makes her even more annoying to the potions department.",
     ["Scientific", "Blunt", "Practical", "Campaigner"],
     [("Lab Safety", "Nathalie is forming a student safety committee. The potions lab is a disgrace."),
      ("Science Crossover", "Other students who see the connection between mundane science and magic.")],
     ["Nathalie filed a formal safety complaint in her first week. It was upheld.", "The potions professor has started wearing safety goggles. Nobody connects this to Nathalie."]),

    ("Erik Dahl (he/him)",
     "Erik is a sculptor who works in magical clay — material that remembers every shape it's been given and can be coaxed into returning to previous forms. His sculptures evolve over time, shifting subtly when no one is watching. He's patient, philosophical, and sees his art as a conversation between intention and material. His workshop smells like earth and rain.",
     ["Artistic", "Patient", "Philosophical", "Quiet"],
     [("Art Students", "Erik offers workshop time to anyone who wants to work with magical materials."),
      ("Exhibition", "He's planning a show of evolving sculptures. Help with curation welcome.")],
     ["Erik's sculptures have been observed moving when the room is empty.", "He created a self-portrait that aged faster than he did."]),

    ("Winnie Okafor (she/her)",
     "Winnie is Emeka's younger sister and desperately wants to be taken seriously on her own merits, not as 'Emeka's little sister.' She's studying Curse-Breaking while he's on the Healer path, which helps. She's fierce, independent, and competitive — especially with Emeka, whom she loves and resents in equal measure.",
     ["Competitive", "Independent", "Fierce", "Determined"],
     [("Curse-Breaking Study Group", "Winnie is forming a study group for practical curse-breaking."),
      ("Sibling Survivors", "Others who share a school with an overachieving older sibling.")],
     ["Winnie solved a curse that stumped her brother.", "She refuses to join any club that Emeka is part of."]),

    ("Bastian Krueger (he/him)",
     "Bastian is a night owl who has built his entire schedule around avoiding sunlight. He takes evening classes, studies at night, and sleeps through morning. This started as a preference and has become a lifestyle. He's sharp, sardonic, and knows more about what happens in the school after midnight than anyone — staff included.",
     ["Nocturnal", "Sardonic", "Observant", "Independent"],
     [("Night Owls", "Bastian runs an unofficial midnight study session in the common room."),
      ("Information Exchange", "He knows what happens after hours. What do you know?")],
     ["Bastian hasn't attended a morning class in six months. His grades are fine.", "He claims to have seen things in the school at night that are better left undiscussed."]),

    ("Lotte Hansen (she/her)",
     "Lotte is a mimic — she can perfectly reproduce any spell she's seen cast once. She can't innovate, but she can copy, and her copies are flawless. This makes her simultaneously the best student in practical classes and the most frustrated student in theoretical ones. She's trying to develop original spellwork and failing, which is a new experience for someone used to perfection.",
     ["Talented", "Frustrated", "Perfectionist", "Hardworking"],
     [("Spellwork Partners", "Lotte wants to practice with creative casters. She'll copy what you do and you can see your technique from outside."),
      ("Theorists", "Help her understand *how* she copies spells. Nobody can explain it, including her.")],
     ["Lotte once perfectly reproduced a professor's signature spell. The professor was not pleased.", "Her ability might be a form of magical synesthesia, but the research is inconclusive."]),

    ("Gabriel Torres (he/him)",
     "Gabriel is a healer who specialises in magical animals, which puts him at a fascinating intersection of creature care and medicine. He runs a small clinic for students' familiars and magical pets, and has earned a reputation for fixing things that the official vet can't. He's gentle, overworked, and running on caffeine and compassion.",
     ["Healer", "Kind", "Overworked", "Dedicated"],
     [("Clinic Volunteers", "Gabriel's animal clinic needs help. Any experience with magical creatures is a bonus."),
      ("Coffee Suppliers", "He's running dangerously low.")],
     ["Gabriel once healed a phoenix, which is supposed to be impossible.", "His clinic operates out of an abandoned classroom that he never officially booked."]),
]
# fmt: on


class Command(BaseCommand):
    help = "Seed 125 additional student castings + character posts for the active run."

    def add_arguments(self, parser):
        parser.add_argument("--run", type=str, help="Run slug (uses first active non-template run if omitted)")

    def handle(self, *args, **options):
        slug = options.get("run")
        from runs.models import Run
        if slug:
            run = Run.objects.get(slug=slug)
        else:
            run = Run.objects.filter(is_template=False, is_active=True).first()
            if not run:
                self.stderr.write("No active run found.")
                return

        houses = list(run.houses.all())
        years = list(run.years.all())
        paths = list(run.paths.all())
        clubs = list(run.clubs.all())
        blood_statuses = list(run.blood_statuses.all())

        if not all([houses, years, paths, blood_statuses]):
            self.stderr.write("Run is missing vocabulary (houses, years, paths, or blood statuses).")
            return

        existing_total = Casting.objects.filter(run=run).count()
        existing_count = Casting.objects.filter(run=run, role="student").count()
        needed = 140 - existing_total
        needed = min(needed, len(CHARACTERS))
        if needed <= 0:
            self.stdout.write(f"Already have enough castings ({existing_count} students). Nothing to do.")
            return

        self.stdout.write(f"Run: {run.name} ({existing_count} existing students)")
        self.stdout.write(f"Creating {needed} new student castings + posts...")

        created = 0
        with transaction.atomic():
            for i, (name, content, keywords, looking_for, rumors) in enumerate(CHARACTERS):
                if created >= needed:
                    break
                # Skip if character already exists in this run
                if Casting.objects.filter(run=run, character_name=name).exists():
                    continue
                # Create user
                email = f"player{i+100}@lfr.test"
                user, user_created = User.objects.get_or_create(
                    email=email,
                    defaults={"role": User.Role.PLAYER},
                )
                if user_created:
                    user.set_password("testpass123")
                    user.save()

                # Assign casting attributes — juniors (year "1") don't get a house
                year = random.choice(years)
                is_junior = year.name in ("1", "1st Year", "Junior")
                house = None if is_junior else random.choice(houses)
                path = random.choice(paths)
                blood = random.choice(blood_statuses)
                player_clubs = random.sample(clubs, k=random.randint(0, min(2, len(clubs))))

                casting = Casting.objects.create(
                    user=user,
                    run=run,
                    role=Casting.Role.STUDENT,
                    character_name=name,
                    house=house,
                    year=year,
                    path=path,
                    blood_status=blood,
                )
                casting.clubs.set(player_clubs)

                # Create post
                post = Post.objects.create(
                    run=run,
                    author=user,
                    casting=casting,
                    post_type=Post.PostType.CHARACTER,
                    content=content,
                    is_published=True,
                )

                # Keywords
                for kw in keywords:
                    PostKeyword.objects.create(post=post, label=kw)

                # Looking for
                for order, (label, desc) in enumerate(looking_for):
                    LookingForEntry.objects.create(
                        post=post, label=label, description=desc, sort_order=order,
                    )

                # Rumors
                for order, text in enumerate(rumors):
                    Rumor.objects.create(post=post, text=text, sort_order=order)

                created += 1

        total = Casting.objects.filter(run=run).count()
        self.stdout.write(self.style.SUCCESS(f"Done. Created {created} students. Total castings: {total}."))
