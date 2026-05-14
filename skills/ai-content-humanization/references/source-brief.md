# Source brief

Derived from item **8) AI Content Humanization** in:
https://gist.github.com/mberman84/065631c62d6d8f30ecb14748c00fc6d9

Original gist intent, condensed:

- Build a text rewriting tool that removes AI-generated artifacts and makes content sound like a real person wrote it.
- Input can be social posts, blog paragraphs, emails, and video scripts.
- Detect common AI tells such as:
  - overused words like `delve`, `landscape`, `leverage`, `it's important to note`, `in conclusion`, `game-changing`, `revolutionary`, `transformative`
  - tone inflation
  - generic phrasing
  - repetitive sentence structures
  - excessive hedging
  - lists that feel too clean and generated
  - identical paragraph lengths and rhythms
- Rewrite by:
  - replacing vague qualifiers with concrete language
  - varying sentence length
  - using contractions and informal phrasing where natural
  - removing filler while keeping the message
  - adding human cadence without introducing errors
- Optional channel tuning:
  - X: punchy and direct
  - LinkedIn: professional but conversational
  - Blog: longer form, opinion and anecdotes allowed
  - Email: brief, clear, warm
- Output the revised text, optionally with notes on what changed.
