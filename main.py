import spacy
from spacy.matcher import Matcher
from spacy.tokens import Token

dose_forms = ["tab", "tabs", "tablet", "tablets", "cap",
              "caps", "capsule", "capsules", "caplet", "caplets"]


def main():
    nlp = spacy.load("en_core_web_sm")

    matcher = Matcher(nlp.vocab)

    def dose_form_getter(token): return token.text in dose_forms
    Token.set_extension("is_dose_form", getter=dose_form_getter)

    dose_with_form_pattern = [
        [
            {"POS": "VERB", "OP": "?"},
            {"LIKE_NUM": True},
            {"LOWER": {"IN": dose_forms}},
        ]
    ]
    matcher.add("DOSE_WITH_FORM", dose_with_form_pattern)

    dose_form_pattern = [{"_": {'is_dose_form': True}}]
    matcher.add('DOSE_FORM', [dose_form_pattern])

    frequencies = [
        [{'LIKE_NUM': True, 'OP': '?'}, {
            'TEXT': {'REGEX': 'a|per|every'}}, {'LOWER': 'day'}],
        [{'LOWER': {'IN': ['once', 'twice', 'thrice']}}, {
            'TEXT': {'REGEX': 'a|per|every'}}, {'LOWER': 'day'}],
        [{'LIKE_NUM': True, 'OP': '?'}, {'LOWER': 'daily'}],
        [{'LOWER': {'REGEX': {'IN': ['b.?i.?d.?', 't.?i.?d.?', 'q.?i.?d.?',
                                     'q.?4.?h.?', 'q.?6.?h.?', 'q.?8.?h.?', 'q.?a.?m.?', 'q.?p.?m.?', 'q.?d.?', 'q.?o.?d.?']}}}]
    ]
    matcher.add('FREQUENCIES', frequencies)

    routes = [
        [{'LOWER': {'REGEX': {'IN': ['oral(ly)?', 'p.?o.?']}}}],
        [{'LOWER': 'by'}, {'LOWER': 'mouth'}],
        [{'LOWER': {
            'REGEX': {'IN': ['nasal(ly)?', 'nostril', 'nare']}}}]
    ]
    matcher.add('ROUTES', routes)

    text = "Take 1 capsule a day by mouth as needed for pain."
    doc = nlp(text)
    matches = matcher(doc)

    # for ent in doc.ents:
    #     # all administration forms here
    #     if ent.label_ in ['TABLET', 'CAPLET', 'CAPSULE', 'PUFF', 'MILLILITER']:
    #         print(f"Entity: {ent.text}, Label: {ent.label_}")

    # this should filter out duplicate matches, e.g. 'twice per day' and 'per day' from 'take 2 tablets twice per day',
    # but note that ChatGPT wrote it.
    filtered_matches = []
    last_end = -1  # Track the end index of the last added match

    # Sort matches by their start index
    matches = sorted(matches, key=lambda x: (x[1], x[2]))

    for match_id, start, end in matches:
        if start >= last_end:  # Ensure no overlap with the previous match
            filtered_matches.append((match_id, start, end))
            last_end = end  # Update the end index

    dose_match = None
    dose_form_match = None  # TODO
    route_match = None
    frequency_match = None

    for match_id, start, end in filtered_matches:
        matched_span = doc[start:end]
        name = nlp.vocab.strings[match_id]
        if name == 'FREQUENCIES':
            startIdx = matched_span[0].idx
            endIdx = startIdx + len(matched_span.text)
            frequency_match = (startIdx, endIdx, 'FREQ')
        if name == "DOSE_WITH_FORM":
            for token in matched_span:
                if token.like_num:
                    dose_match = (token.idx, token.idx + len(token.text), 'DOSE')
                if token._.is_dose_form:
                    dose_form_match = (token.idx, token.idx + len(token.text), 'DOSE_FORM')
        if name == 'ROUTES':
            startIdx = matched_span[0].idx
            endIdx = startIdx + len(matched_span.text)
            route_match = (startIdx, endIdx, 'ROUTE')

    # TODO: only write if all matches are defined
    # if (dose_match is not None and dose_form_match is not None and route_match is not None and frequency_match is not None):
    if (True):
        print(text, '\n', dose_match, dose_form_match, route_match, frequency_match)
        # with open('data.txt', 'w') as file:
        #     file.write(f'({text}, [{dose_match}, {dose_form_match}, {route_match}, {frequency_match}])')
    else:
        print('TODO: write to separate file')


if __name__ == "__main__":
    main()
