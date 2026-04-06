"""Seed student castings + character posts from extracted CoW23 Facebook group data."""
import random
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import User
from casting.models import Casting
from posts.models import LookingForEntry, Post, PostKeyword, Rumor

COW23_DIR = Path(__file__).resolve().parent.parent.parent.parent / "example" / "cow23"

# Posts that are character introductions (manually curated from extraction).
# Maps post directory name -> (character_name, role).
# role is one of: "student", "professor", "staff", "headmaster"
# fmt: off
CHARACTER_POSTS = {
    "post_01_your_last_minute_alchemy_professor": ("Rook Sharpshade (she/her)", "professor"),
    "post_03_name_leon_oakley": ("Leon Oakley", "student"),
    "post_05_last_second_but_still_worth_putting_up_i": ("Cécile Bregendahl (she/her)", "student"),
    "post_06_lexie_bouquet_sheher": ("Lexie Bouquet (she/her)", "student"),
    "post_07_last_updated_mar3_3_villain_extra_sprink": ("Scarlett Crimson Vanderberg (she/her)", "student"),
    "post_09_better_late_than_never": ("Archibald 'Archie' Kowalski (he/him)", "student"),
    "post_10_what_did_you_think_of_vincent_lloyd": ("Vincent Lloyd", "student"),
    "post_13_cecil_december_de_mon": ("Cecil December de Mon", "professor"),
    "post_14_freaking_news": ("Guillaume Froissard de Bersaillin", "student"),
    "post_15_well_better_very_late_then_never_so_here": ("Archibald Kowalski", "student"),
    "post_16_victoria_lloyd_lloyd": ("Victoria Lloyd (she/her)", "student"),
    "post_18_riley_blake_sheher": ("Riley Blake (she/her)", "student"),
    "post_19_will_post_a_decent_picture_soon": ("Zack Character", "student"),
    "post_20_dr_anastasia_lambert_sheher": ("Dr Anastasia Lambert (she/her)", "professor"),
    "post_24_name_briar_derosiers": ("Briar Derosiers (she/her)", "student"),
    "post_25_supporting_character_cryptozoology_tutor": ("Cryptozoology Tutor", "professor"),
    "post_26_apollonia_justitia_prima_de_dampierre_he": ("Apollonia Justitia Prima de Dampierre (she/her)", "student"),
    "post_27_what_do_you_need": ("The Voice", "student"),
    "post_28_aiden_thorenz": ("Aiden Thorenz (he/him)", "student"),
    "post_29_kiara_williams_sheher": ("Kiara Williams (she/her)", "student"),
    "post_30_priscilla_jade_grimwolph": ("Priscilla Jade Grimwolph", "student"),
    "post_31_inaris_dal": ("Inaris Dal", "student"),
    "post_32_damasile_danae_decourcelle_sheher": ("Damasile Danae Decourcelle (she/her)", "student"),
    "post_33_meet_professor_alfred_nice": ("Professor Alfred Nice", "professor"),
    "post_34_invocation_professor_monitor_of_house_se": ("Invocation Professor", "professor"),
    "post_35_name_gennevieve_gilly_duval_sheher": ("Gennevieve 'Gilly' Duval (she/her)", "student"),
    "post_36_algernon_algie_griffiths": ("Algernon 'Algie' Griffiths", "student"),
    "post_37_alastair_cain": ("Alastair Cain", "student"),
    "post_38_rose_garrett": ("Rose Garrett", "student"),
    "post_39_joanna_lerman_sheher": ("Joanna Lerman (she/her)", "student"),
    "post_40_valentina_isabella_marlene_schertz": ("Valentina Isabella Marlene Schertz", "student"),
    "post_42_amber_rose_mayweather": ("Amber Rose Mayweather", "student"),
    "post_43_character_name_sigismund_sparks_hehim": ("Sigismund Sparks (he/him)", "student"),
    "post_44_latecomer_lfr": ("Latecomer Character", "student"),
    "post_47_nadia_stendahl": ("Nadia Stendahl", "student"),
    "post_48_professor_morrigan_grymm_sheher": ("Professor Morrigan Grymm (she/her)", "professor"),
    "post_49_enid_hayes_sheher_theythem": ("Enid Hayes (she/her; they/them)", "student"),
    "post_51_name_nyx_eilerts": ("Nyx Eilerts (she/her)", "student"),
    "post_52_aurel_farkas": ("Aurel Farkas", "student"),
    "post_53_the_dreamweaver_family_a_pair_of_twins_w": ("The Dreamweaver Family", "student"),
    "post_54_sophie_holbrook": ("Sophie Holbrook", "student"),
    "post_55_david_salo": ("David Salo", "student"),
    "post_56_prof_percival_alberic_cogwell_percy": ("Prof. Percival Alberic Cogwell (he/him)", "professor"),
    "post_57_headmistress_celestyna_wolska_sheher": ("Headmistress Celestyna Wolska (she/her)", "headmaster"),
    "post_58_raphael_strohlicht": ("Raphael Strohlicht", "student"),
    "post_59_hector_greenbottom": ("Hector Greenbottom", "student"),
    "post_60_supporting_character": ("Supporting Character (Laura)", "student"),
    "post_61_skyler_von_faust": ("Skyler von Faust", "student"),
    "post_64_diane_danielle_decourcelle_the_fifth": ("Diane Danielle Decourcelle the Fifth", "student"),
    "post_65_aristide_carter": ("Aristide Carter", "student"),
    "post_66_nora_vargas": ("Nora Vargas", "student"),
    "post_68_kristoff_von_faust": ("Kristoff Von Faust", "student"),
    "post_69_updated_060220": ("Dean Murray Character", "student"),
    "post_70_tiberius_septimius_augustus_lázár_de_szá": ("Tiberius Lázár", "student"),
    "post_71_endellion_fire_soul_hughes": ("Endellion 'Fire Soul' Hughes", "student"),
    "post_72_professor_greenbottom_has_been_dead_and": ("Professor Greenbottom (ghost)", "professor"),
    "post_73_rory_aurora_darrow": ("Rory (Aurora) Darrow", "student"),
    "post_74_character_name_valentino_schertz_hehim": ("Valentino Schertz (he/him)", "student"),
    "post_75_lavea_decourcelle_beaumont": ("Lavea Decourcelle-Beaumont", "student"),
    "post_78_senya_corvi": ("Senya Corvi", "student"),
    "post_79_this_is_a_supporting_character": ("Supporting Character (Anna)", "student"),
    "post_81_looking_for_relations": ("Cæcilie Bregendal", "student"),
    "post_82_updated": ("Kim Autumn Character", "student"),
    "post_83_guillaume_froissard_de_bersaillin_update": ("Guillaume Froissard de Bersaillin (updated)", "student"),
    "post_84_ferio_metellus": ("Ferio Metellus", "student"),
    "post_85_hello_hello_hello": ("Anzelika Character", "student"),
    "post_86_ill_put_up_a_proper_lfr_soon_but_i_figur": ("Mia Character", "student"),
    "post_88_name_fairbrooks_like_madonna_or_prince": ("Fairbrooks", "student"),
}
# fmt: on

ROLE_MAP = {
    "student": "student",
    "professor": "professor",
    "staff": "staff",
    "headmaster": "headmaster",
}


def read_post_body(post_dir):
    """Read and return the body content from a post.md file."""
    md_path = post_dir / "post.md"
    if not md_path.exists():
        return ""
    text = md_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Find body start (after ---)
    body_start = 0
    for i, line in enumerate(lines):
        if line.startswith("---"):
            body_start = i + 1
            break

    # Body ends at ## Images or ## Comments
    body_lines = []
    for line in lines[body_start:]:
        if line.startswith("## Images") or line.startswith("## Comments"):
            break
        body_lines.append(line)

    return "\n".join(body_lines).strip()


def extract_keywords_from_body(body):
    """Try to extract keywords from the post body."""
    keywords = []
    # Look for **Keywords:** or **Main concepts:** lines
    for pattern in [
        r"\*\*Keywords?:?\s*\*\*\s*(.+)",
        r"\*\*Main concepts?:?\s*\*\*\s*(.+)",
        r"\*\*Characteristics?:?\s*\*\*\s*(.+)",
        r"\*\*Keyword:?\s*\*\*\s*(.+)",
    ]:
        m = re.search(pattern, body, re.IGNORECASE)
        if m:
            raw = m.group(1).strip()
            # Split on commas
            kws = [k.strip().strip("*").strip() for k in raw.split(",")]
            keywords.extend(k for k in kws if k and len(k) < 40)
            break

    return keywords[:6]  # Cap at 6 keywords


def extract_looking_for(body):
    """Try to extract looking_for entries from the post body."""
    entries = []
    # Look for **Looking for:** sections with bullet points or bold labels
    looking_section = ""
    in_section = False
    for line in body.split("\n"):
        lower = line.lower().strip()
        if "looking for" in lower and ("**" in line or "##" in line):
            in_section = True
            continue
        if in_section:
            if line.startswith("**") and ":" in line and not line.startswith("**Background"):
                # Bold label line like **Friends:** description
                m = re.match(r"\*\*(.+?):?\s*\*\*\s*[-:]?\s*(.*)", line)
                if m:
                    label = m.group(1).strip()
                    desc = m.group(2).strip()
                    if label.lower() not in ("looking for", "background", "i'm open"):
                        entries.append((label, desc))
            elif line.startswith("##") or line.startswith("**Background"):
                break

    return entries[:5]  # Cap at 5


class Command(BaseCommand):
    help = "Seed castings and character posts from CoW23 Facebook group data"

    def add_arguments(self, parser):
        parser.add_argument("--run", type=str, help="Run slug (uses first active non-template run if omitted)")

    def handle(self, *args, **options):
        if not COW23_DIR.exists():
            self.stderr.write(f"CoW23 data directory not found: {COW23_DIR}")
            self.stderr.write("Run 'python example/extract_cow23.py' first.")
            return

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
        teaching_subjects = list(run.teaching_subjects.all())

        if not all([houses, years, paths, blood_statuses]):
            self.stderr.write("Run is missing vocabulary (houses, years, paths, or blood statuses).")
            return

        created = 0
        skipped = 0
        with transaction.atomic():
            for i, (dir_name, (char_name, role_str)) in enumerate(CHARACTER_POSTS.items()):
                post_dir = COW23_DIR / dir_name
                if not post_dir.exists():
                    self.stderr.write(f"  Skipping {dir_name}: directory not found")
                    skipped += 1
                    continue

                # Skip if character already exists in this run
                if Casting.objects.filter(run=run, character_name=char_name).exists():
                    self.stdout.write(f"  Skipping {char_name}: already exists")
                    skipped += 1
                    continue

                body = read_post_body(post_dir)
                if not body:
                    self.stderr.write(f"  Skipping {dir_name}: empty body")
                    skipped += 1
                    continue

                # Create user
                email = f"cow23_{i}@lfr.test"
                user, user_created = User.objects.get_or_create(
                    email=email,
                    defaults={"role": User.Role.PLAYER},
                )
                if user_created:
                    user.set_password("testpass123")
                    user.save()

                # Determine casting role
                casting_role = getattr(Casting.Role, role_str.upper(), Casting.Role.STUDENT)

                # Assign casting attributes
                year = random.choice(years)
                is_junior = year.name in ("1", "1st Year", "Junior")
                house = None if is_junior else random.choice(houses)
                path = random.choice(paths)
                blood = random.choice(blood_statuses)
                player_clubs = random.sample(clubs, k=random.randint(0, min(2, len(clubs))))

                casting_kwargs = {
                    "user": user,
                    "run": run,
                    "role": casting_role,
                    "character_name": char_name,
                    "house": house,
                    "year": year,
                    "path": path,
                    "blood_status": blood,
                }

                # Professors get teaching subjects instead of year/path
                if role_str == "professor":
                    casting_kwargs["year"] = None
                    casting_kwargs["path"] = None
                    if teaching_subjects:
                        casting_kwargs["teaching_subject"] = random.choice(teaching_subjects)
                elif role_str == "headmaster":
                    casting_kwargs["year"] = None
                    casting_kwargs["path"] = None

                casting = Casting.objects.create(**casting_kwargs)
                if role_str == "student":
                    casting.clubs.set(player_clubs)

                # Determine post type
                post_type = Post.PostType.CHARACTER

                post = Post.objects.create(
                    run=run,
                    author=user,
                    casting=casting,
                    post_type=post_type,
                    content=body,
                    is_published=True,
                )

                # Extract and create keywords
                keywords = extract_keywords_from_body(body)
                for kw in keywords:
                    PostKeyword.objects.create(post=post, label=kw)

                # Extract and create looking_for entries
                looking_for = extract_looking_for(body)
                for order, (label, desc) in enumerate(looking_for):
                    LookingForEntry.objects.create(
                        post=post, label=label, description=desc, sort_order=order,
                    )

                created += 1
                kw_count = len(keywords)
                lf_count = len(looking_for)
                self.stdout.write(f"  Created: {char_name} ({role_str}) [{kw_count} kw, {lf_count} lf]")

        total = Casting.objects.filter(run=run).count()
        self.stdout.write(self.style.SUCCESS(
            f"\nDone. Created {created} characters, skipped {skipped}. Total castings: {total}."
        ))
