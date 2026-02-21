#!/usr/bin/env bash
#
# Seed candidate events for the Civil War topic.
# Creates a harvest batch and inserts 5 candidate events for testing the approval workflow.
#
# Usage: ./backend/scripts/seed_candidates.sh [API_BASE_URL]
#   API_BASE_URL defaults to http://localhost:8000

set -euo pipefail

API="${1:-http://localhost:8000}"
TOPIC_SLUG="civil_war"

echo "=== Seeding candidate events ==="
echo "API: $API"

# --- Register/login to get a token ---
# Try to register (ignore error if user already exists)
curl -sf -X POST "$API/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email":"seed-admin@lessonlines.dev","password":"seedpass123","display_name":"Seed Admin"}' \
  > /dev/null 2>&1 || true

TOKEN=$(curl -sf -X POST "$API/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=seed-admin@lessonlines.dev&password=seedpass123' \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

AUTH="Authorization: Bearer $TOKEN"

# --- Get topic ID ---
TOPIC_ID=$(curl -sf "$API/api/topics" \
  | python3 -c "
import sys, json
topics = json.load(sys.stdin)
t = next((t for t in topics if t['slug'] == '$TOPIC_SLUG'), None)
if not t:
    print('ERROR: topic not found', file=sys.stderr)
    sys.exit(1)
print(t['id'])
")
echo "Topic: $TOPIC_SLUG ($TOPIC_ID)"

# --- Create harvest batch ---
BATCH=$(curl -sf -X POST "$API/api/admin/harvest-batches" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d "{
    \"topic_id\": \"$TOPIC_ID\",
    \"source_name\": \"Wikipedia\",
    \"source_url\": \"https://en.wikipedia.org/wiki/American_Civil_War\",
    \"strategy\": \"manual_seed\"
  }")

BATCH_ID=$(echo "$BATCH" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
echo "Created harvest batch: $BATCH_ID"

# --- Bulk-create 5 candidate events ---
RESULT=$(curl -sf -X POST "$API/api/admin/candidates/batch" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d "{
  \"batch_id\": \"$BATCH_ID\",
  \"candidates\": [
    {
      \"topic_id\": \"$TOPIC_ID\",
      \"title\": \"Battle of Shiloh\",
      \"description\": \"A major battle in the Western Theater fought April 6-7, 1862 in southwestern Tennessee. Union forces under Ulysses S. Grant withstood a surprise Confederate attack led by Albert Sidney Johnston, who was killed in the fighting. The battle's nearly 24,000 casualties shocked the nation and dispelled illusions of a quick war.\",
      \"date_start\": \"1862-04-06\",
      \"date_end\": \"1862-04-07\",
      \"date_display\": \"April 6-7, 1862\",
      \"date_precision\": \"day\",
      \"location\": \"Pittsburg Landing, Tennessee\",
      \"latitude\": 35.1492,
      \"longitude\": -88.3265,
      \"significance\": \"One of the bloodiest early battles; demonstrated the war would be long and costly.\",
      \"source_url\": \"https://en.wikipedia.org/wiki/Battle_of_Shiloh\",
      \"source_name\": \"Wikipedia\",
      \"image_url\": \"https://upload.wikimedia.org/wikipedia/commons/thumb/2/21/Thure_de_Thulstrup_-_Battle_of_Shiloh.jpg/800px-Thure_de_Thulstrup_-_Battle_of_Shiloh.jpg\",
      \"confidence_score\": 0.95
    },
    {
      \"topic_id\": \"$TOPIC_ID\",
      \"title\": \"Battle of Fredericksburg\",
      \"description\": \"Fought December 11-15, 1862, in and around Fredericksburg, Virginia. Confederate General Robert E. Lee's forces decisively defeated Union attacks led by Ambrose Burnside. Repeated frontal assaults against entrenched Confederates on Marye's Heights resulted in devastating Union casualties.\",
      \"date_start\": \"1862-12-11\",
      \"date_end\": \"1862-12-15\",
      \"date_display\": \"December 11-15, 1862\",
      \"date_precision\": \"day\",
      \"location\": \"Fredericksburg, Virginia\",
      \"latitude\": 38.3032,
      \"longitude\": -77.4605,
      \"significance\": \"A major Confederate victory that led to a crisis of confidence in Union leadership.\",
      \"source_url\": \"https://en.wikipedia.org/wiki/Battle_of_Fredericksburg\",
      \"source_name\": \"Wikipedia\",
      \"image_url\": \"https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/Gallant_Charge_of_Humphrey%27s_Division_at_the_Battle_of_Fredericksburg_LCCN2004661366_%28cropped%29.jpg/800px-Gallant_Charge_of_Humphrey%27s_Division_at_the_Battle_of_Fredericksburg_LCCN2004661366_%28cropped%29.jpg\",
      \"confidence_score\": 0.93
    },
    {
      \"topic_id\": \"$TOPIC_ID\",
      \"title\": \"Battle of Chancellorsville\",
      \"description\": \"Fought April 30 - May 6, 1863 near Spotsylvania County, Virginia. Often considered Robert E. Lee's greatest victory, the battle saw Lee divide his outnumbered army and execute a daring flanking attack by Stonewall Jackson. However, the Confederate victory was pyrrhic—Jackson was mortally wounded by friendly fire.\",
      \"date_start\": \"1863-04-30\",
      \"date_end\": \"1863-05-06\",
      \"date_display\": \"April 30 – May 6, 1863\",
      \"date_precision\": \"day\",
      \"location\": \"Spotsylvania County, Virginia\",
      \"latitude\": 38.3048,
      \"longitude\": -77.6488,
      \"significance\": \"Lee's tactical masterpiece, but the loss of Stonewall Jackson was a blow the Confederacy never recovered from.\",
      \"source_url\": \"https://en.wikipedia.org/wiki/Battle_of_Chancellorsville\",
      \"source_name\": \"Wikipedia\",
      \"image_url\": \"https://upload.wikimedia.org/wikipedia/commons/thumb/7/76/Battle_of_Chancellorsville.png/800px-Battle_of_Chancellorsville.png\",
      \"confidence_score\": 0.96
    },
    {
      \"topic_id\": \"$TOPIC_ID\",
      \"title\": \"Battle of Chickamauga\",
      \"description\": \"Fought September 19-20, 1863 in northwestern Georgia, this was the most significant Union defeat in the Western Theater and the second-bloodiest battle of the entire war after Gettysburg. A Confederate breakthrough routed much of the Union army, though General George Thomas's stubborn defense earned him the nickname 'Rock of Chickamauga.'\",
      \"date_start\": \"1863-09-19\",
      \"date_end\": \"1863-09-20\",
      \"date_display\": \"September 19-20, 1863\",
      \"date_precision\": \"day\",
      \"location\": \"Chickamauga, Georgia\",
      \"latitude\": 34.9188,
      \"longitude\": -85.2607,
      \"significance\": \"Largest Confederate victory in the West; led to the Siege of Chattanooga.\",
      \"source_url\": \"https://en.wikipedia.org/wiki/Battle_of_Chickamauga\",
      \"source_name\": \"Wikipedia\",
      \"image_url\": \"https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Unbekannt_-_Confederate_General_Hood_wounded_at_the_battle_of_Chickamauga_American_Civil_War_-_%28MeisterDrucke-739711%29.jpg/800px-Unbekannt_-_Confederate_General_Hood_wounded_at_the_battle_of_Chickamauga_American_Civil_War_-_%28MeisterDrucke-739711%29.jpg\",
      \"confidence_score\": 0.94
    },
    {
      \"topic_id\": \"$TOPIC_ID\",
      \"title\": \"Battle of the Wilderness\",
      \"description\": \"Fought May 5-7, 1864 in Orange and Spotsylvania counties, Virginia. The first battle between Ulysses S. Grant and Robert E. Lee, fought in dense forest that neutralized the Union's numerical advantage and caused fires that trapped wounded soldiers. Unlike previous Union commanders, Grant did not retreat after the bloody stalemate but pressed south.\",
      \"date_start\": \"1864-05-05\",
      \"date_end\": \"1864-05-07\",
      \"date_display\": \"May 5-7, 1864\",
      \"date_precision\": \"day\",
      \"location\": \"Orange County, Virginia\",
      \"latitude\": 38.3185,
      \"longitude\": -77.7473,
      \"significance\": \"Marked the start of Grant's Overland Campaign and a new Union strategy of relentless pressure.\",
      \"source_url\": \"https://en.wikipedia.org/wiki/Battle_of_the_Wilderness\",
      \"source_name\": \"Wikipedia\",
      \"image_url\": \"https://upload.wikimedia.org/wikipedia/commons/thumb/e/ee/Genl._U.S._Grant_at_Wilderness_LCCN2004661535_%28cropped%29.jpg/800px-Genl._U.S._Grant_at_Wilderness_LCCN2004661535_%28cropped%29.jpg\",
      \"confidence_score\": 0.95
    }
  ]
}")

COUNT=$(echo "$RESULT" | python3 -c "import sys,json; print(len(json.load(sys.stdin)))")
echo "Created $COUNT candidate events"

# --- Mark batch as completed ---
curl -sf -X PATCH "$API/api/admin/harvest-batches/$BATCH_ID" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"status": "completed"}' > /dev/null

echo ""
echo "=== Done ==="
echo "Harvest batch: $BATCH_ID (completed)"
echo "Candidates: $COUNT pending review"
echo ""
echo "View at: $API/docs#/admin"
