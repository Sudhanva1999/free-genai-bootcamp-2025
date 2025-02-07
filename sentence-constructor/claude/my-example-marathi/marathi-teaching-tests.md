<test-cases>
    <case id="simple-1">
        <english>I eat bread.</english>
        <vocabulary>
            <word>
                <marathi>खाणे</marathi>
                <phonetic>khane</phonetic>
                <english>eat</english>
            </word>
            <word>
                <marathi>ब्रेड</marathi>
                <phonetic>bread</phonetic>
                <english>bread</english>
            </word>
        </vocabulary>
        <structure>[Subject] [Object] [Verb].</structure>
        <considerations>
            - Basic sentence with subject, object, and verb
            - Present tense form
            - Subject can be omitted in Marathi
        </considerations>
    </case>
    <case id="simple-2">
        <english>The book is red.</english>
        <vocabulary>
            <word>
                <marathi>पुस्तक</marathi>
                <phonetic>pustak</phonetic>
                <english>book</english>
            </word>
            <word>
                <marathi>लाल</marathi>
                <phonetic>lal</phonetic>
                <english>red</english>
            </word>
        </vocabulary>
        <structure>[Subject] [Adjective].</structure>
        <considerations>
            - Simple descriptor sentence
            - Uses adjective directly
            - No verb needed in Marathi
        </considerations>
    </case>
</test-cases>

### 1.2 Compound Sentences
```xml
<test-cases>
    <case id="compound-1">
        <english>I eat bread and drink water.</english>
        <vocabulary>
            <word>
                <marathi>खाणे</marathi>
                <phonetic>khane</phonetic>
                <english>eat</english>
            </word>
            <word>
                <marathi>ब्रेड</marathi>
                <phonetic>bread</phonetic>
                <english>bread</english>
            </word>
            <word>
                <marathi>पिणे</marathi>
                <phonetic>pine</phonetic>
                <english>drink</english>
            </word>
            <word>
                <marathi>पाणी</marathi>
                <phonetic>pani</phonetic>
                <english>water</english>
            </word>
        </vocabulary>
        <structure>[Subject] [Object1] [Verb1], [Object2] [Verb2].</structure>
        <considerations>
            - Compound sentence with two actions
            - Subject shared between clauses
            - Uses "आणि" for connection
        </considerations>
    </case>
</test-cases>

### 1.3 Complex Sentences
```xml
<test-cases>
    <case id="complex-1">
        <english>Because it's hot, I drink water.</english>
        <vocabulary>
            <word>
                <marathi>गरम</marathi>
                <phonetic>garam</phonetic>
                <english>hot</english>
            </word>
            <word>
                <marathi>पिणे</marathi>
                <phonetic>pine</phonetic>
                <english>drink</english>
            </word>
            <word>
                <marathi>पाणी</marathi>
                <phonetic>pani</phonetic>
                <english>water</english>
            </word>
        </vocabulary>
        <structure>[Reason] [Subject] [Object] [Verb].</structure>
        <considerations>
            - Cause and effect relationship
            - Uses "म्हणून" for "because"
            - Weather description
        </considerations>
    </case>
</test-cases>

## 2. Vocabulary Edge Cases

### 2.1 Multiple Meanings
```xml
<vocabulary-test>
    <word>
        <marathi>लागणे</marathi>
        <phonetic>lagne</phonetic>
        <meanings>
            <meaning>to take (time)</meaning>
            <meaning>to cost (money)</meaning>
            <meaning>to be attached (to something)</meaning>
        </meanings>
        <test-sentences>
            <sentence>How long does it take?</sentence>
            <sentence>How much does it cost?</sentence>
            <sentence>The picture hangs on the wall.</sentence>
        </test-sentences>
    </word>
</vocabulary-test>

### 2.2 Transitive/Intransitive Pairs
```xml
<vocabulary-test>
    <pair>
        <transitive>
            <marathi>उघडणे</marathi>
            <phonetic>ughadne</phonetic>
            <english>to open (something)</english>
        </transitive>
        <intransitive>
            <marathi>उघडणे</marathi>
            <phonetic>ughadne</phonetic>
            <english>to open (by itself)</english>
        </intransitive>
        <test-sentences>
            <sentence>I open the door.</sentence>
            <sentence>The door opens.</sentence>
        </test-sentences>
    </pair>
</vocabulary-test>

## 3. State Transition Tests

### 3.1 Valid Transitions
```xml
<transition-test>
    <scenario id="setup-to-attempt">
        <initial-state>Setup</initial-state>
        <input>मी ब्रेड खातो.</input>
        <expected-state>Attempt</expected-state>
        <validation>
            - Input contains Marathi text
            - No question marks
            - Contains vocabulary from setup
        </validation>
    </scenario>
    <scenario id="attempt-to-clues">
        <initial-state>Attempt</initial-state>
        <input>How do I use postpositions?</input>
        <expected-state>Clues</expected-state>
        <validation>
            - Input is a question
            - References grammar concept
            - Related to previous attempt
        </validation>
    </scenario>
</transition-test>

### 3.2 Invalid Transitions
```xml
<transition-test>
    <scenario id="invalid-clues-to-setup">
        <initial-state>Clues</initial-state>
        <input>Can you give me the answer?</input>
        <expected-response>
            - Reminder that answers aren't provided
            - Offer additional clues
            - Encourage attempt
        </expected-response>
    </scenario>
</transition-test>

## 4. Teaching Scenario Tests

### 4.1 Common Mistakes
```xml
<teaching-test>
    <scenario id="postposition-mistake">
        <student-attempt>मी शाळेला जातो.</student-attempt>
        <error>Incorrect use of ला postposition for regular actions</error>
        <expected-guidance>
            - Acknowledge attempt
            - Explain ला vs त without giving answer
            - Encourage new attempt
        </expected-guidance>
    </scenario>
    <scenario id="verb-conjugation-mistake">
        <student-attempt>मी खाला.</student-attempt>
        <error>Incorrect verb conjugation</error>
        <expected-guidance>
            - Point out verb type
            - Review past tense formation rules
            - Encourage correction
        </expected-guidance>
    </scenario>
</teaching-test>

## 5. Validation Criteria

### 5.1 Response Scoring
```xml
<scoring-criteria>
    <category name="vocabulary-table">
        <criteria>
            - Contains all necessary words (2 points)
            - Correct formatting (2 points)
            - Dictionary forms only (2 points)
            - No postposition inclusion (2 points)
            - Appropriate difficulty level (2 points)
        </criteria>
    </category>
    <category name="sentence-structure">
        <criteria>
            - Clear bracketed format (2 points)
            - No conjugations shown (2 points)
            - Appropriate for level (2 points)
            - Matches example patterns (2 points)
            - No postpositions included (2 points)
        </criteria>
    </category>
</scoring-criteria>

## 6. Documentation Improvements

### 6.1 Cross-References
```xml
<cross-references>
    <reference id="postpositions">
        <related-sections>
            - Vocabulary Table Guidelines
            - Common Mistakes
            - Teaching Scenarios
        </related-sections>
        <purpose>Ensure consistent postposition handling across documentation</purpose>
    </reference>
    <reference id="verb-conjugation">
        <related-sections>
            - Sentence Structure Guidelines
            - Teaching Scenarios
            - Validation Criteria
        </related-sections>
        <purpose>Maintain consistent verb form handling</purpose>
    </reference>
</cross-references>