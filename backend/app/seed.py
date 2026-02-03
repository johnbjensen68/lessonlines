"""
Database seeding script for LessonLines.
Run with: python -m app.seed
"""
import uuid
from datetime import date
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .models import (
    Topic,
    Tag,
    CurriculumFramework,
    CurriculumStandard,
    Event,
    event_tags,
    event_standards,
)


def seed_topics(db: Session) -> dict[str, Topic]:
    topics_data = [
        {
            "slug": "civil_war",
            "name": "American Civil War",
            "description": "Key events from 1861-1865, including causes, major battles, and aftermath of the American Civil War.",
        },
        {
            "slug": "american_revolution",
            "name": "American Revolution",
            "description": "Events leading to and including the American Revolution (1775-1783).",
        },
        {
            "slug": "world_war_2",
            "name": "World War II",
            "description": "Major events of World War II from 1939-1945, focusing on American involvement.",
        },
    ]

    topics = {}
    for data in topics_data:
        topic = Topic(**data)
        db.add(topic)
        topics[data["slug"]] = topic

    db.flush()
    return topics


def seed_tags(db: Session) -> dict[str, Tag]:
    tags_data = [
        {"name": "military", "category": "theme"},
        {"name": "political", "category": "theme"},
        {"name": "social", "category": "theme"},
        {"name": "economic", "category": "theme"},
        {"name": "diplomatic", "category": "theme"},
        {"name": "cultural", "category": "theme"},
        {"name": "battle", "category": "type"},
        {"name": "treaty", "category": "type"},
        {"name": "declaration", "category": "type"},
        {"name": "legislation", "category": "type"},
        {"name": "assassination", "category": "type"},
    ]

    tags = {}
    for data in tags_data:
        tag = Tag(**data)
        db.add(tag)
        tags[data["name"]] = tag

    db.flush()
    return tags


def seed_frameworks(db: Session) -> dict[str, CurriculumFramework]:
    frameworks_data = [
        {
            "code": "CCSS",
            "name": "Common Core State Standards",
            "state": None,
            "subject": "English Language Arts & Literacy in History/Social Studies",
            "grade_levels": "6-12",
        },
        {
            "code": "AP_USH",
            "name": "AP US History",
            "state": None,
            "subject": "History",
            "grade_levels": "9-12",
        },
        {
            "code": "TEKS",
            "name": "Texas Essential Knowledge and Skills",
            "state": "TX",
            "subject": "Social Studies",
            "grade_levels": "K-12",
        },
    ]

    frameworks = {}
    for data in frameworks_data:
        framework = CurriculumFramework(**data)
        db.add(framework)
        frameworks[data["code"]] = framework

    db.flush()
    return frameworks


def seed_standards(db: Session, frameworks: dict[str, CurriculumFramework]) -> dict[str, CurriculumStandard]:
    standards_data = [
        # Common Core
        {
            "framework": "CCSS",
            "code": "CCSS.ELA-LITERACY.RH.6-8.1",
            "title": "Cite specific textual evidence",
            "description": "Cite specific textual evidence to support analysis of primary and secondary sources.",
            "grade_level": "6-8",
            "strand": "Reading",
        },
        {
            "framework": "CCSS",
            "code": "CCSS.ELA-LITERACY.RH.6-8.2",
            "title": "Determine central ideas",
            "description": "Determine the central ideas or information of a primary or secondary source.",
            "grade_level": "6-8",
            "strand": "Reading",
        },
        {
            "framework": "CCSS",
            "code": "CCSS.ELA-LITERACY.RH.9-10.3",
            "title": "Analyze key events",
            "description": "Analyze in detail a series of events described in a text; determine whether earlier events caused later ones.",
            "grade_level": "9-10",
            "strand": "Reading",
        },
        {
            "framework": "CCSS",
            "code": "CCSS.ELA-LITERACY.RH.11-12.7",
            "title": "Integrate multiple sources",
            "description": "Integrate and evaluate multiple sources of information presented in diverse formats.",
            "grade_level": "11-12",
            "strand": "Reading",
        },
        # AP US History
        {
            "framework": "AP_USH",
            "code": "AP.USH.5.1",
            "title": "Slavery and Sectional Conflict",
            "description": "Explain the causes of the Civil War including the expansion of slavery.",
            "grade_level": "HS",
            "strand": "Period 5",
        },
        {
            "framework": "AP_USH",
            "code": "AP.USH.5.2",
            "title": "The Civil War",
            "description": "Explain how the Civil War was fought and the consequences of the war.",
            "grade_level": "HS",
            "strand": "Period 5",
        },
        {
            "framework": "AP_USH",
            "code": "AP.USH.3.1",
            "title": "Colonial Independence",
            "description": "Explain the causes of the American Revolution.",
            "grade_level": "HS",
            "strand": "Period 3",
        },
        {
            "framework": "AP_USH",
            "code": "AP.USH.7.1",
            "title": "World War II",
            "description": "Explain the causes and consequences of American involvement in World War II.",
            "grade_level": "HS",
            "strand": "Period 7",
        },
        # Texas TEKS
        {
            "framework": "TEKS",
            "code": "TEKS.8.1.A",
            "title": "Identify major causes of Civil War",
            "description": "Identify the major eras and events in U.S. history through 1877, including the Civil War.",
            "grade_level": "8",
            "strand": "History",
        },
        {
            "framework": "TEKS",
            "code": "TEKS.8.4.C",
            "title": "Explain American Revolution causes",
            "description": "Explain the issues surrounding important events of the American Revolution.",
            "grade_level": "8",
            "strand": "History",
        },
        {
            "framework": "TEKS",
            "code": "TEKS.US.7.A",
            "title": "WWII causes and effects",
            "description": "Identify reasons for U.S. involvement in World War II.",
            "grade_level": "HS",
            "strand": "History",
        },
    ]

    standards = {}
    for data in standards_data:
        framework = frameworks[data.pop("framework")]
        standard = CurriculumStandard(framework_id=framework.id, **data)
        db.add(standard)
        standards[standard.code] = standard

    db.flush()
    return standards


def seed_civil_war_events(db: Session, topic: Topic, tags: dict, standards: dict) -> list[Event]:
    events_data = [
        {
            "title": "Attack on Fort Sumter",
            "description": "Confederate forces bombarded Fort Sumter in Charleston Harbor, South Carolina, marking the beginning of the Civil War. After 34 hours of bombardment, Major Robert Anderson surrendered the fort.",
            "date_start": date(1861, 4, 12),
            "date_end": date(1861, 4, 13),
            "date_display": "April 12-13, 1861",
            "location": "Charleston, South Carolina",
            "significance": "The attack on Fort Sumter unified the North and prompted Lincoln to call for 75,000 volunteers, officially beginning the Civil War.",
            "tags": ["military", "battle"],
            "standards": ["CCSS.ELA-LITERACY.RH.9-10.3", "AP.USH.5.2", "TEKS.8.1.A"],
        },
        {
            "title": "First Battle of Bull Run",
            "description": "The first major land battle of the Civil War, fought near Manassas, Virginia. Confederate forces, reinforced by troops arriving by rail, routed the Union army.",
            "date_start": date(1861, 7, 21),
            "date_display": "July 21, 1861",
            "location": "Manassas, Virginia",
            "significance": "The Confederate victory shattered Northern hopes for a quick end to the war and demonstrated that the conflict would be long and costly.",
            "tags": ["military", "battle"],
            "standards": ["AP.USH.5.2", "TEKS.8.1.A"],
        },
        {
            "title": "Battle of Antietam",
            "description": "The bloodiest single-day battle in American history, with approximately 23,000 casualties. General McClellan's Army of the Potomac halted Lee's first invasion of the North.",
            "date_start": date(1862, 9, 17),
            "date_display": "September 17, 1862",
            "location": "Sharpsburg, Maryland",
            "significance": "The Union victory gave Lincoln the opportunity to issue the Preliminary Emancipation Proclamation and kept Britain and France from recognizing the Confederacy.",
            "tags": ["military", "battle", "political"],
            "standards": ["CCSS.ELA-LITERACY.RH.9-10.3", "AP.USH.5.2"],
        },
        {
            "title": "Emancipation Proclamation",
            "description": "President Lincoln issued the Emancipation Proclamation, declaring all slaves in Confederate-held territory to be forever free, effective January 1, 1863.",
            "date_start": date(1862, 9, 22),
            "date_display": "September 22, 1862",
            "location": "Washington, D.C.",
            "significance": "Transformed the war from a conflict to preserve the Union into a war to end slavery, preventing European intervention and allowing African Americans to serve in the Union Army.",
            "tags": ["political", "social", "declaration"],
            "standards": ["CCSS.ELA-LITERACY.RH.6-8.2", "AP.USH.5.1", "TEKS.8.1.A"],
        },
        {
            "title": "Battle of Gettysburg",
            "description": "The largest battle of the Civil War and a turning point, fought over three days in southern Pennsylvania. Lee's second invasion of the North ended in a decisive Confederate defeat.",
            "date_start": date(1863, 7, 1),
            "date_end": date(1863, 7, 3),
            "date_display": "July 1-3, 1863",
            "location": "Gettysburg, Pennsylvania",
            "significance": "The Union victory ended Confederate hopes of winning the war through a military victory in the North and marked the beginning of the Confederacy's decline.",
            "tags": ["military", "battle"],
            "standards": ["CCSS.ELA-LITERACY.RH.9-10.3", "AP.USH.5.2", "TEKS.8.1.A"],
        },
        {
            "title": "Siege of Vicksburg",
            "description": "Union forces under General Grant besieged the Confederate fortress city of Vicksburg, Mississippi, gaining control of the Mississippi River after the city's surrender.",
            "date_start": date(1863, 5, 18),
            "date_end": date(1863, 7, 4),
            "date_display": "May 18 - July 4, 1863",
            "location": "Vicksburg, Mississippi",
            "significance": "The fall of Vicksburg gave the Union complete control of the Mississippi River, splitting the Confederacy in two.",
            "tags": ["military", "battle"],
            "standards": ["AP.USH.5.2"],
        },
        {
            "title": "Gettysburg Address",
            "description": "President Lincoln delivered a brief but powerful speech at the dedication of the Soldiers' National Cemetery at Gettysburg, redefining the purpose of the war.",
            "date_start": date(1863, 11, 19),
            "date_display": "November 19, 1863",
            "location": "Gettysburg, Pennsylvania",
            "significance": "The address redefined the Civil War as a struggle for equality and democracy, becoming one of the most quoted speeches in American history.",
            "tags": ["political", "declaration"],
            "standards": ["CCSS.ELA-LITERACY.RH.6-8.1", "CCSS.ELA-LITERACY.RH.11-12.7"],
        },
        {
            "title": "Sherman's March to the Sea",
            "description": "General William T. Sherman led Union forces on a devastating march from Atlanta to Savannah, Georgia, destroying Confederate infrastructure and supplies.",
            "date_start": date(1864, 11, 15),
            "date_end": date(1864, 12, 21),
            "date_display": "November 15 - December 21, 1864",
            "location": "Georgia",
            "significance": "The march demonstrated the Union's ability to wage total war and helped break Southern morale and will to continue fighting.",
            "tags": ["military"],
            "standards": ["AP.USH.5.2"],
        },
        {
            "title": "Lee Surrenders at Appomattox",
            "description": "General Robert E. Lee surrendered the Army of Northern Virginia to General Ulysses S. Grant at Appomattox Court House, effectively ending the Civil War.",
            "date_start": date(1865, 4, 9),
            "date_display": "April 9, 1865",
            "location": "Appomattox Court House, Virginia",
            "significance": "Lee's surrender marked the end of major military operations and began the process of reuniting the nation.",
            "tags": ["military", "political", "treaty"],
            "standards": ["CCSS.ELA-LITERACY.RH.9-10.3", "AP.USH.5.2", "TEKS.8.1.A"],
        },
        {
            "title": "Assassination of Abraham Lincoln",
            "description": "President Abraham Lincoln was shot by John Wilkes Booth while attending a play at Ford's Theatre. He died the following morning.",
            "date_start": date(1865, 4, 14),
            "date_display": "April 14, 1865",
            "location": "Washington, D.C.",
            "significance": "Lincoln's assassination deeply affected the nation's mourning and complicated Reconstruction efforts under his successor, Andrew Johnson.",
            "tags": ["political", "assassination"],
            "standards": ["CCSS.ELA-LITERACY.RH.6-8.2", "AP.USH.5.2"],
        },
        {
            "title": "13th Amendment Ratified",
            "description": "The 13th Amendment to the Constitution was ratified, formally abolishing slavery throughout the United States.",
            "date_start": date(1865, 12, 6),
            "date_display": "December 6, 1865",
            "location": "United States",
            "significance": "The amendment permanently ended the institution of slavery in the United States and laid the groundwork for civil rights legislation.",
            "tags": ["political", "social", "legislation"],
            "standards": ["CCSS.ELA-LITERACY.RH.11-12.7", "AP.USH.5.1", "TEKS.8.1.A"],
        },
    ]

    events = []
    for data in events_data:
        tag_names = data.pop("tags")
        standard_codes = data.pop("standards")

        event = Event(topic_id=topic.id, **data)
        db.add(event)
        db.flush()

        # Add tags
        for tag_name in tag_names:
            if tag_name in tags:
                db.execute(event_tags.insert().values(event_id=event.id, tag_id=tags[tag_name].id))

        # Add standards
        for code in standard_codes:
            if code in standards:
                db.execute(event_standards.insert().values(event_id=event.id, standard_id=standards[code].id))

        events.append(event)

    return events


def seed_revolution_events(db: Session, topic: Topic, tags: dict, standards: dict) -> list[Event]:
    events_data = [
        {
            "title": "Boston Massacre",
            "description": "British soldiers fired into a crowd of colonists in Boston, killing five people. The incident became a rallying point for anti-British sentiment.",
            "date_start": date(1770, 3, 5),
            "date_display": "March 5, 1770",
            "location": "Boston, Massachusetts",
            "significance": "The Boston Massacre became a powerful propaganda tool for colonial activists and helped unite colonists against British rule.",
            "tags": ["political", "military"],
            "standards": ["AP.USH.3.1", "TEKS.8.4.C"],
        },
        {
            "title": "Boston Tea Party",
            "description": "Colonial activists, disguised as Mohawk Indians, dumped 342 chests of British tea into Boston Harbor to protest taxation without representation.",
            "date_start": date(1773, 12, 16),
            "date_display": "December 16, 1773",
            "location": "Boston, Massachusetts",
            "significance": "The Tea Party provoked harsh British retaliation and helped push the colonies toward independence.",
            "tags": ["political", "economic"],
            "standards": ["CCSS.ELA-LITERACY.RH.6-8.2", "AP.USH.3.1", "TEKS.8.4.C"],
        },
        {
            "title": "Battles of Lexington and Concord",
            "description": "British troops marched to confiscate colonial weapons but were met by armed minutemen. The 'shot heard round the world' began the Revolutionary War.",
            "date_start": date(1775, 4, 19),
            "date_display": "April 19, 1775",
            "location": "Lexington and Concord, Massachusetts",
            "significance": "These battles marked the beginning of armed conflict between Britain and the American colonies.",
            "tags": ["military", "battle"],
            "standards": ["CCSS.ELA-LITERACY.RH.9-10.3", "AP.USH.3.1", "TEKS.8.4.C"],
        },
        {
            "title": "Declaration of Independence",
            "description": "The Continental Congress adopted the Declaration of Independence, written primarily by Thomas Jefferson, formally announcing separation from Britain.",
            "date_start": date(1776, 7, 4),
            "date_display": "July 4, 1776",
            "location": "Philadelphia, Pennsylvania",
            "significance": "The Declaration established the philosophical foundation for American democracy and inspired independence movements worldwide.",
            "tags": ["political", "declaration"],
            "standards": ["CCSS.ELA-LITERACY.RH.6-8.1", "CCSS.ELA-LITERACY.RH.11-12.7", "AP.USH.3.1", "TEKS.8.4.C"],
        },
        {
            "title": "Washington Crosses the Delaware",
            "description": "General George Washington led Continental Army forces across the icy Delaware River on Christmas night for a surprise attack on Hessian forces at Trenton.",
            "date_start": date(1776, 12, 25),
            "date_display": "December 25, 1776",
            "location": "Delaware River",
            "significance": "The victory at Trenton boosted American morale after a series of defeats and helped save the Continental Army.",
            "tags": ["military", "battle"],
            "standards": ["AP.USH.3.1"],
        },
        {
            "title": "Battle of Saratoga",
            "description": "American forces defeated British General Burgoyne's army in upstate New York, marking a major turning point in the war.",
            "date_start": date(1777, 9, 19),
            "date_end": date(1777, 10, 7),
            "date_display": "September 19 - October 7, 1777",
            "location": "Saratoga, New York",
            "significance": "The American victory convinced France to enter the war as an ally, providing crucial military and financial support.",
            "tags": ["military", "battle", "diplomatic"],
            "standards": ["CCSS.ELA-LITERACY.RH.9-10.3", "AP.USH.3.1"],
        },
        {
            "title": "Valley Forge Winter Camp",
            "description": "The Continental Army endured a brutal winter encampment at Valley Forge, suffering from cold, disease, and lack of supplies.",
            "date_start": date(1777, 12, 19),
            "date_end": date(1778, 6, 19),
            "date_display": "December 1777 - June 1778",
            "location": "Valley Forge, Pennsylvania",
            "significance": "Despite terrible conditions, the army emerged stronger and better trained under Baron von Steuben's leadership.",
            "tags": ["military"],
            "standards": ["AP.USH.3.1"],
        },
        {
            "title": "France Allies with America",
            "description": "France formally recognized American independence and signed treaties of alliance and commerce with the United States.",
            "date_start": date(1778, 2, 6),
            "date_display": "February 6, 1778",
            "location": "Paris, France",
            "significance": "French support provided crucial military assistance, including troops, ships, and financing that helped win the war.",
            "tags": ["diplomatic", "political", "treaty"],
            "standards": ["CCSS.ELA-LITERACY.RH.6-8.2", "AP.USH.3.1"],
        },
        {
            "title": "Battle of Yorktown",
            "description": "Combined American and French forces besieged British General Cornwallis at Yorktown, Virginia, forcing his surrender.",
            "date_start": date(1781, 9, 28),
            "date_end": date(1781, 10, 19),
            "date_display": "September 28 - October 19, 1781",
            "location": "Yorktown, Virginia",
            "significance": "Cornwallis's surrender effectively ended major military operations and led to peace negotiations.",
            "tags": ["military", "battle"],
            "standards": ["CCSS.ELA-LITERACY.RH.9-10.3", "AP.USH.3.1", "TEKS.8.4.C"],
        },
        {
            "title": "Treaty of Paris",
            "description": "The Treaty of Paris officially ended the Revolutionary War, with Britain recognizing American independence and establishing borders.",
            "date_start": date(1783, 9, 3),
            "date_display": "September 3, 1783",
            "location": "Paris, France",
            "significance": "The treaty established the United States as an independent nation and set its boundaries from the Atlantic to the Mississippi River.",
            "tags": ["diplomatic", "political", "treaty"],
            "standards": ["CCSS.ELA-LITERACY.RH.11-12.7", "AP.USH.3.1", "TEKS.8.4.C"],
        },
    ]

    events = []
    for data in events_data:
        tag_names = data.pop("tags")
        standard_codes = data.pop("standards")

        event = Event(topic_id=topic.id, **data)
        db.add(event)
        db.flush()

        for tag_name in tag_names:
            if tag_name in tags:
                db.execute(event_tags.insert().values(event_id=event.id, tag_id=tags[tag_name].id))

        for code in standard_codes:
            if code in standards:
                db.execute(event_standards.insert().values(event_id=event.id, standard_id=standards[code].id))

        events.append(event)

    return events


def seed_ww2_events(db: Session, topic: Topic, tags: dict, standards: dict) -> list[Event]:
    events_data = [
        {
            "title": "Germany Invades Poland",
            "description": "Nazi Germany invaded Poland, beginning World War II in Europe. Britain and France declared war on Germany two days later.",
            "date_start": date(1939, 9, 1),
            "date_display": "September 1, 1939",
            "location": "Poland",
            "significance": "The invasion triggered the start of World War II and demonstrated the effectiveness of German blitzkrieg tactics.",
            "tags": ["military", "battle"],
            "standards": ["AP.USH.7.1", "TEKS.US.7.A"],
        },
        {
            "title": "Attack on Pearl Harbor",
            "description": "Japan launched a surprise military strike on the U.S. naval base at Pearl Harbor, Hawaii, killing over 2,400 Americans and destroying much of the Pacific Fleet.",
            "date_start": date(1941, 12, 7),
            "date_display": "December 7, 1941",
            "location": "Pearl Harbor, Hawaii",
            "significance": "The attack brought the United States into World War II and unified American public opinion for war.",
            "tags": ["military", "battle"],
            "standards": ["CCSS.ELA-LITERACY.RH.9-10.3", "AP.USH.7.1", "TEKS.US.7.A"],
        },
        {
            "title": "U.S. Declares War",
            "description": "Following President Roosevelt's 'Day of Infamy' speech, Congress declared war on Japan. Germany and Italy then declared war on the United States.",
            "date_start": date(1941, 12, 8),
            "date_display": "December 8, 1941",
            "location": "Washington, D.C.",
            "significance": "American entry into the war transformed the conflict into a truly global war and ultimately tipped the balance toward Allied victory.",
            "tags": ["political", "declaration"],
            "standards": ["CCSS.ELA-LITERACY.RH.6-8.2", "AP.USH.7.1", "TEKS.US.7.A"],
        },
        {
            "title": "Battle of Midway",
            "description": "U.S. Navy forces defeated a Japanese attack on Midway Atoll, sinking four Japanese aircraft carriers and turning the tide in the Pacific War.",
            "date_start": date(1942, 6, 4),
            "date_end": date(1942, 6, 7),
            "date_display": "June 4-7, 1942",
            "location": "Midway Atoll, Pacific Ocean",
            "significance": "The victory at Midway ended Japanese naval superiority and put the U.S. on the offensive in the Pacific.",
            "tags": ["military", "battle"],
            "standards": ["AP.USH.7.1"],
        },
        {
            "title": "D-Day Invasion",
            "description": "Allied forces launched the largest amphibious invasion in history on the beaches of Normandy, France, beginning the liberation of Western Europe.",
            "date_start": date(1944, 6, 6),
            "date_display": "June 6, 1944",
            "location": "Normandy, France",
            "significance": "D-Day opened a second front in Europe and began the final push to defeat Nazi Germany.",
            "tags": ["military", "battle"],
            "standards": ["CCSS.ELA-LITERACY.RH.9-10.3", "AP.USH.7.1", "TEKS.US.7.A"],
        },
        {
            "title": "Battle of the Bulge",
            "description": "Germany launched a major surprise offensive through the Ardennes forest, creating a 'bulge' in Allied lines before being pushed back.",
            "date_start": date(1944, 12, 16),
            "date_end": date(1945, 1, 25),
            "date_display": "December 16, 1944 - January 25, 1945",
            "location": "Ardennes, Belgium/Luxembourg",
            "significance": "The failed German offensive depleted Nazi resources and hastened the end of the war in Europe.",
            "tags": ["military", "battle"],
            "standards": ["AP.USH.7.1"],
        },
        {
            "title": "Iwo Jima",
            "description": "U.S. Marines captured the strategic island of Iwo Jima after intense fighting. The iconic flag-raising on Mount Suribachi became a symbol of American sacrifice.",
            "date_start": date(1945, 2, 19),
            "date_end": date(1945, 3, 26),
            "date_display": "February 19 - March 26, 1945",
            "location": "Iwo Jima, Japan",
            "significance": "The capture of Iwo Jima provided a base for fighter escorts and emergency landings for B-29 bombers attacking Japan.",
            "tags": ["military", "battle"],
            "standards": ["AP.USH.7.1"],
        },
        {
            "title": "Germany Surrenders (V-E Day)",
            "description": "Nazi Germany surrendered unconditionally to the Allied forces, ending World War II in Europe.",
            "date_start": date(1945, 5, 8),
            "date_display": "May 8, 1945",
            "location": "Berlin, Germany",
            "significance": "V-E Day marked the end of the Nazi regime and allowed the Allies to focus resources on defeating Japan.",
            "tags": ["military", "political", "treaty"],
            "standards": ["CCSS.ELA-LITERACY.RH.11-12.7", "AP.USH.7.1"],
        },
        {
            "title": "Atomic Bomb Dropped on Hiroshima",
            "description": "The United States dropped an atomic bomb on Hiroshima, Japan, killing approximately 80,000 people instantly and many more from radiation.",
            "date_start": date(1945, 8, 6),
            "date_display": "August 6, 1945",
            "location": "Hiroshima, Japan",
            "significance": "The first use of nuclear weapons in warfare demonstrated their devastating power and hastened Japan's surrender.",
            "tags": ["military"],
            "standards": ["CCSS.ELA-LITERACY.RH.6-8.2", "AP.USH.7.1", "TEKS.US.7.A"],
        },
        {
            "title": "Japan Surrenders (V-J Day)",
            "description": "Japan announced its surrender following the atomic bombings of Hiroshima and Nagasaki, ending World War II.",
            "date_start": date(1945, 8, 15),
            "date_display": "August 15, 1945",
            "location": "Tokyo, Japan",
            "significance": "Japan's surrender ended World War II and began the American occupation and reconstruction of Japan.",
            "tags": ["military", "political", "treaty"],
            "standards": ["CCSS.ELA-LITERACY.RH.11-12.7", "AP.USH.7.1", "TEKS.US.7.A"],
        },
    ]

    events = []
    for data in events_data:
        tag_names = data.pop("tags")
        standard_codes = data.pop("standards")

        event = Event(topic_id=topic.id, **data)
        db.add(event)
        db.flush()

        for tag_name in tag_names:
            if tag_name in tags:
                db.execute(event_tags.insert().values(event_id=event.id, tag_id=tags[tag_name].id))

        for code in standard_codes:
            if code in standards:
                db.execute(event_standards.insert().values(event_id=event.id, standard_id=standards[code].id))

        events.append(event)

    return events


def run_seed():
    """Main seeding function."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Check if already seeded
        existing_topics = db.query(Topic).count()
        if existing_topics > 0:
            print("Database already seeded. Skipping...")
            return

        print("Seeding topics...")
        topics = seed_topics(db)

        print("Seeding tags...")
        tags = seed_tags(db)

        print("Seeding curriculum frameworks...")
        frameworks = seed_frameworks(db)

        print("Seeding curriculum standards...")
        standards = seed_standards(db, frameworks)

        print("Seeding Civil War events...")
        seed_civil_war_events(db, topics["civil_war"], tags, standards)

        print("Seeding American Revolution events...")
        seed_revolution_events(db, topics["american_revolution"], tags, standards)

        print("Seeding World War II events...")
        seed_ww2_events(db, topics["world_war_2"], tags, standards)

        db.commit()
        print("Database seeding complete!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    run_seed()
