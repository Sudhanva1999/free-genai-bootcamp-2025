Extract ALL Marathi vocabulary from the provided text. For each word:

1. Include EVERY word from the text:
   - Nouns (नाम)
   - Verbs (क्रियापद)
   - Adjectives (विशेषण)
   - Adverbs (क्रियाविशेषण)

2. Ignore grammar or fixed expressions:
   - Postpositions (प्रत्यय)
   - Fixed expressions (वाक्प्रचार)

3. Break down each word into its parts:
   - Individual Devanagari components
   - Romanized reading for each part
   - English meaning

Format each word exactly like the example provided:
```
{
    "marathi": "पैसे देणे",
    "phonetic": "Paisē dēṇē",
    "english": "to pay",
    "parts": [
      { "marathi": "पैसे", "phonetic": ["Paisē"] },
      { "marathi": "देणे", "phonetic": ["dēṇē"] }
    ]
}
```

Important:
- Do not skip any words, even common ones
- Convert words to their dictionary form
- Break down compound words into their parts
- Make sure romanization is accurate for each part