<examples>
<example>
    <user:input>
        Bears are at the door, did you leave the garbage out?
    </user:input>
    <score>7</score>
    <score_reasons>
    - BAD: Too many clues and considerations, limit to 5 clues/considerations
    - BAD: the beginner sentence is uncessary, should jsut start showing the vocabulary table
    - BAD: In the clues we should not provide the polite form of verbs, because the student needs to figure that out.
    - BAD: The sentence structure says too much we really want something that is conceptual like this: [Location] [Subject] [Verb], [Object] [Verb-past]?
    </score_reasons>
    <assistant:state>
        setup
    </assistant:state>
    <assistant:output>
        I'll help you translate this sentence to Marathi! Let me break this down for you.
        Vocabulary Table:
        | Word | Marathi |  
        |------|----------|
        | bear | अस्वल | 
        | door | दार |
        | garbage | कचरा | 
        | to put/leave | ठेवणे |
        
        Basic Sentence Structure:
        [Location] [Subject] [Object] [Verb Question]

        Clues, Considerations, Next Steps:
        - This sentence combines both a statement and a question
        - In Marathi, questions often end with "का" (ka)
        - The word "are" needs to be expressed using "आहे" but you'll need to figure out if it's singular or plural
        - For "at the door", you'll need to use the correct postposition
        - Think about whether you want to use formal or informal "you"
        - The verb "ठेवणे" (leave/put) will need to be conjugated for past tense
        - Consider starting with just one part of the sentence first - either the statement about bears or the question about garbage

        Would you like to make an attempt at either part of the sentence?
</assistant:output>
</example>

<example>
    <user:input>
        Bears are at the door, did you leave the garbage out?
    </user:input>
    <score>6</score>
    <score_reasons>
            - BAD: Limit number of positive reinforcement, too many compliments on simple correct usage.
            - BAD: Dont break in parts, evaluate the sentence as a whole. 
    </score_reasons>
    <assistant:state>
        Attempt
    </assistant:state>
    <assistant:output>
       Let me break down what you wrote:
            Part 1: "अस्वल दारावर आले आहेत" = "Bears have come at the door"

            You correctly used the plural form for bears
            Good use of "वर" postposition with "दार" (दारावर = at the door)
            Nice use of plural past tense "आले आहेत"

            Part 2: "तू कचरा बाहेर टाकला का?" = "Did you throw the garbage outside?"

            Good use of informal "तू" for "you"
            Excellent use of "का" for forming the question
            You used "टाकला" (to throw) instead of "ठेवणे" (to put/leave) - this is actually more natural in Marathi!
            Nice addition of "बाहेर" (outside) which makes the sentence more precise

            Overall, this is an excellent translation that sounds very natural in Marathi! The sentence structure, tenses, and particles are all correct. Would you like to try another sentence?
</assistant:output>
</example>

<example>
    <user:input>
        we all go to school
    </user:input>
    <score>5</score>
    <score_reasons>
            - BAD: Don't directly give away the answer , do not show the correct form of the word
            - BAD: Use a similar words for clue instead of using the same word asked about in the question.
    </score_reasons>
    <assistant:state>
        Clues
    </assistant:state>
    <assistant:output>
       Current State: Clues
        Here are some helpful points about using शाळा:
        When indicating movement towards school, we use शाळेत
        When saying "to school", we use शाळेला
        The base word शाळा changes to शाळे when adding these postpositions
        For this sentence where we're talking about going TO school, शाळेत or शाळेला would both work:
        शाळेत is more common and general "in/to school"
        शाळेला specifically emphasizes movement towards school
        Think about which one feels more natural for expressing "going to school" as a regular activity. Would you like to try forming the sentence now?
</assistant:output>
</example>

<example>
    <user:input>
         we all go to school
    </user:input>
    <score>3</score>
    <score_reasons>
    - BAD: Incorrectly detecting plural forms: The word 'जातो' is correctly translated, but the feedback suggests changing it to the same word ('जातो'). No change is needed here.
    </score_reasons>
     <assistant:state>
        Attempt
    </assistant:state>
    <assistant:output>
        Current State: Attempt
        Let me break down what you wrote:
        "आम्ही सगळे शाळेला जातो" = "We all go to school"
        Almost perfect! Just one small adjustment needed:

        Since you're using "आम्ही सगळे" (we all), the verb should be plural form
        "जातो" is singular form
        You need to use "जातो" → "जातो"

        Your sentence structure is excellent:

        Perfect use of "आम्ही सगळे" for "we all"
        Correct spelling of "शाळेला" this time
        Good word order following Subject-Object-Verb

        Would you like to try once more with the correct verb form?
</example>

<example>
    <user:input>
         we play with ball
    </user:input>
    <score>3</score>
    <score_reasons>
    - BAD: Incorrectly detecting plural forms: The word 'खेळतो' is correctly translated, but the feedback suggests changing it to the same word ('खेळतो'). No change is needed here. The word is already in plural form.
    </score_reasons>
     <assistant:state>
        Attempt
    </assistant:state>
    <assistant:output>
        Current State: Attempt
        Let me analyze your attempt:
        "आम्ही चेंडूने खेळतो" = "We play with ball"
        Getting closer! Let's look at what you've done:

        Perfect use of "ने" with "चेंडू" to show "with the ball"
        Excellent word order following Subject-Object-Verb
        You're still using "खेळतो" which is singular form
        Remember that since "आम्ही" is plural (we), the verb needs to match

        Consider:

        When "we" do something, how does the verb ending change?
        Think about other verbs you know with "आम्ही" - what ending do they use?

        Would you like to try one more time focusing on the verb form?
</example>

<example>
    <user:input>
        we play with ball
    </user:input>
    <score>10</score>
    <score_reasons>
    - GOOD: Concise to the point response
    - GOOD: Good correct sentense structure provided.
    </score_reasons>
    <assistant:state>
        setup
    </assistant:state>
    <assistant:output>
        I'll help you translate this sentence to Marathi! Let me break this down for you.
        Vocabulary Table:
        | Word | Marathi |  
        |------|----------|
        | play | खेळणे | 
        | ball | चेंडू |
        | we | आम्ही | 
        
       Basic Sentence Structure:
        [Subject] [Object] [Verb]
        Clues, Considerations, Next Steps:

        - Think about whether we're playing right now or in general
        - Consider how the word "with" changes into a postposition in Marathi
        - The verb will need to match with "we" (plural subject)
        - To show "with ball", you'll need to use the correct case ending
        - Focus first on getting the basic structure: who is doing what

        Would you like to try forming the sentence?
</assistant:output>
</example>

</examples>
