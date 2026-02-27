---
name: build-topic
description: Creates a topic file of events for the lessonlines application
disable-model-invocation: true
---
Generate a new event data JSON file for the topic: $ARGUMENTS

Follow these steps:

1. Look at the existing files in `backend/event-data/` to understand the exact format required.

2. Generate a JSON file for the topic with:
   - A `topic` object with `slug`, `name`, and `description`
   - Create events at a granularity so that the topic has at least 100 events
   - Each event must have: `id` (slug like `evt_<short_name>`), `title`, `description`, `date_start` (YYYY-MM-DD), `date_display`, `date_precision`, `location`, `significance`, `image_url`, `tags`, `standards`
   - `date_end` only if the event spans multiple days
   - `tags` should be from: military, battle, political, social, economic, exploration, science, legislation, treaty, declaration, assassination
   - `standards` should reference real CCSS.ELA-LITERACY, AP.USH/APWH/APGOV, or TEKS standards relevant to the topic

3. For image URLs: use Wikimedia Commons. Fetch the correct URL using the Commons API to verify each file exists and get its thumbnail URL:
   ```
   curl -s -A "LessonLinesBot/1.0" "https://commons.wikimedia.org/w/api.php?action=query&titles=File:<filename>&prop=imageinfo&iiprop=url&iiurlwidth=300&format=json"
   ```
   Use the returned `url` field to construct the 300px thumbnail:
   `https://upload.wikimedia.org/wikipedia/commons/thumb/<hash>/<filename>/300px-<filename>`
   Make sure all images are freely licensed (public domain or Creative Commons). Verify in batches of up to 20 files at a time using the pipe-separated `titles` parameter.

4. Write the file to `backend/event-data/<topic_slug>.json`

5. Use the image validation script to confirm all URLs resolve correctly:
   Fix any issues reported before finishing.

