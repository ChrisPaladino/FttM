#### Tourney
- https://brackethq.com/b/x5n6b/

#### Implement
- Hot Box:
    - Need to implement ALLY and FOE in the Wrestler JSON
- Explain how Signature is resolved?
    - We may need to have In-Control only for the 1 previous FAC, not a running total.
    - An alternative is that the Signature gives more points to whoever was in control
- Helped doesnt resolve properly if there's text and no points...
      {
        "id": 39,
        "control": false,
        "type": "Helped",
        "text": "Go to HIGHLIGHT REEL \"G\", \"M\" or \"V\" depending on the source of help."
      },
      {
        "id": 40,
        "control": false,
        "type": "Helped",
        "text": "Go to HIGHLIGHT REEL \"G\", \"M\" or \"V\" depending on the source of help."
      },
- Submission cards: moves break on 1-3 (1-4 if STRONG)
    - Confirm Submission works - why are we getting TV Grade?
- Editor needs images
- Wild Card / Highlight reel cards
    - Need to distinguish which skills are mental vs. physical
- Test of Strength cards: results (if both STRONG and/or POWERFUL)
     - 1-2: Face scores 1 point
     - 3-4: Ref breaks hold
     - 5-6: Heel scores 1 point

    - Verify this works, our underdog is STRONG: Star, so I suspect she CAN use the card
        Card drawn: Test of Strength (No Control)
        Card type: Test of Strength
        Favored can use: False
        Underdog can use: False
        Neither wrestler can use this skill. No points scored.
- HELP that makes you roll on the TYPE chart
    - G = gang/group
    - M = manager
    - V = valet
- Digitize the various charts
- Implement the Pre and Post match charts
- Ranking and pointing of wrestlers
     - https://www.reddit.com/r/FaceToTheMat/comments/noje6j/homebrew_fttm_overall_rating_based_on_attributes/
- Contracts
     - https://www.reddit.com/r/FaceToTheMat/comments/nm9hk7/houserules_face_to_the_mat_wrestler_contracts/
- Age / Retirement

#### Experiments
- In control should ONLY look at the last card, not look at the last scoring wrestler
    - I want to experiment with this rule - whoever last scored is in_control, not just the last card.
    - Note: Signature DOES still use the previous card