# AI + Human Collaboration - Presentation

This folder contains the Slidev presentation for "AI + Human Collaboration".

## How to Run

To start the presentation locally, open your terminal in this directory and run:

```bash
npx slidev slide.md
```

Or if you have `slidev` installed globally:

```bash
slidev slide.md
```

This will start the development server, usually at `http://localhost:3030`.

### Troubleshooting
If you are running from the project root (`c:\Coding\soengkanel.github.io`), `npx` might fail because the `slidev` package is located in the `slide/` folder, not the root.

**Recommended:** Navigate to the `slide` folder first:
```bash
cd slide
npx slidev ai-human-collaboration/slide.md
```

Or navigating directly to this folder:
```bash
cd slide/ai-human-collaboration
npx slidev slide.md
```

## Structure

- `slide.md`: The main markdown file containing the slides.
- `public/`: Assets directory for images and resources.
