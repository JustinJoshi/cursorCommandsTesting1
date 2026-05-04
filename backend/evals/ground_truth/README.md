# Ground Truth Dataset

Place your annotated screenshot/JSON pairs here to run evaluations.

## Format

For each test case, provide two files with matching names:
- `listing_001.png` — Screenshot of Facebook Marketplace search results
- `listing_001.json` — JSON array of expected extracted listings

## JSON Schema

```json
[
  {
    "title": "2019 Toyota Prius LE",
    "price": 18500,
    "year": 2019,
    "model": "Prius",
    "trim": "LE",
    "mileage": 45000,
    "description": "Clean title, one owner, regular maintenance",
    "link_text": null
  }
]
```

## Creating Ground Truth

1. Open Facebook Marketplace and search "Toyota Prius"
2. Take a screenshot (use the app's capture, or manually)
3. Save the screenshot as `listing_XXX.png`
4. Manually create the corresponding JSON with correct extracted values
5. Repeat for 20-30 diverse examples (different layouts, prices, years)

## Tips

- Include edge cases: listings with missing info, unusual prices, non-Prius results mixed in
- Include both search results pages and individual listing detail pages
- Vary the screenshot size/resolution to test robustness
