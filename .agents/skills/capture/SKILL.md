---
name: capture
description: Save something into the second brain's inbox (00-inbox/) without processing it. Use when the owner shares a URL, pastes text, a transcript, or an idea and says "save this", "clip this", "add to inbox", "remember this article", or wants to keep something for later. Does not write wiki pages; hand off to the ingest skill if the owner wants it processed now.
---

# Capture: anything → 00-inbox/

Goal: get the material into the vault fast, faithfully, with enough metadata for a later ingest.
Capture never touches `20-wiki/`, `index.md`, or `10-raw/`.

## Steps

1. **Identify the input**
   - URL: fetch the page and convert to clean markdown (main content only, no nav/ads/comments).
     If fetching fails or is paywalled, save the URL plus whatever the owner pasted, and say so.
   - Video URL: if `yt-dlp` is available, get title/channel/date and the transcript
     (`yt-dlp --skip-download --write-auto-subs --sub-format vtt`); otherwise ask the owner to paste the transcript.
   - Pasted text / idea / transcript: use it verbatim.
   - File path: if it is already in `00-inbox/`, there is nothing to do. Otherwise copy (don't move) it into `00-inbox/`.
2. **Write** `00-inbox/YYYY-MM-DD-short-title.md` (today's date, kebab-case, at most 6 words):
   ```markdown
   ---
   captured: YYYY-MM-DD
   source_type: article | paper | video | podcast | transcript | note | idea | other
   title: Original Title
   author:
   published:
   url:
   why: "<the owner's reason for saving it, if given>"
   ---

   <content, verbatim. Do not summarize, rewrite, or "clean up" claims>
   ```
   Never overwrite an existing inbox file; add `-2` to the name if it is taken.
3. **Images** referenced by the page: download to `10-raw/assets/` only if the owner asks or they carry
   essential information (charts, diagrams). Link them with relative paths.
4. **Report** in one line: the file path, plus "say *ingest it* to process now".

## Rules
- Verbatim over pretty. Capture is a copy, not an interpretation.
- No `log.md` entry (nothing in the knowledge layer changed).
- If the owner says "save and ingest", run capture, then follow the `ingest` skill on the new file.
