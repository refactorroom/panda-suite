# Saved documents

**Saved output.** Save a new document under
`.panda-suite/docs/<story-slug>/YYYY-MM-DD-<topic>.<ext>` in the active project
root. Create one folder per documentation story, named from the requested
document's subject or purpose as a short lowercase hyphenated slug (for example,
`integrations` for a guide about integrations); keep artifacts for the same story
together. Infer the story from the request and its source context only when they
identify it clearly. If the story is unclear or multiple stories fit, ask the user
to select a story before saving; do not create a guessed or generic folder. Use the
current local date and a short lowercase hyphenated topic for the file name. Use
Markdown unless
the user asks for another format such as `.docx` or `.pdf`; then keep the Markdown
source beside the exported file. Convert with tools already available; if none
can produce the format, save the Markdown, state that the export was not created,
and ask before installing anything. An explicit path or file name, an existing
document named for update, or a chat-only request takes precedence. In a workspace
with several projects, use the one the request or its sources identify; ask when
several still fit. Do not overwrite another document; choose a distinct name.
After writing or updating a document, keep its story folder and all existing
contents under `.panda-suite/docs/`; do not remove them as cleanup.
