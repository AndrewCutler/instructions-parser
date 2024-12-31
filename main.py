import spacy
from spacy.matcher import Matcher

def main():
    nlp = spacy.load("en_core_web_sm")

    matcher = Matcher(nlp.vocab)

    admin_forms = ["tab", "tabs", "tablet", "tablets", "cap",
                   "caps", "capsule", "capsules", "caplet", "caplets"]

    dose_adminform_pattern = [
        [
            {"POS": "VERB", "OP": "?"},
            {"LIKE_NUM": True},
            {"LOWER": {"IN": admin_forms}},
        ]
    ]

    matcher.add("DOSE_ADMINFORM", dose_adminform_pattern)

    dose_number = [[{"LIKE_NUM": True}]]
    matcher.add('DOSE', dose_number)

    daily_frequencies = [
        [{'LIKE_NUM': True, 'OP': '?'}, {
            'TEXT': {'REGEX': 'a|per|every'}}, {'LOWER': 'day'}],
        [{'LIKE_NUM': True, 'OP': '?'}, {'LEMMA': 'daily'}]
    ]
    matcher.add('DAILY_FREQUENCIES', daily_frequencies)

    ruler = nlp.add_pipe('entity_ruler', before='ner')

    # case-insensitive regex
    administration_forms = [
        {'label': 'TABLET', 'pattern': [
            {'TEXT': {'REGEX': '(?i)tab(let)?(s)?'}}]},
        {'label': 'CAPLET', 'pattern': [
            {'TEXT': {'REGEX': '(?i)caplet(s)?'}}]},
        {'label': 'CAPSULE', 'pattern': [
            {'TEXT': {'REGEX': '(?i)cap(sule)(s)?'}}]},
        {'label': 'PUFF', 'pattern': [{'TEXT': {'REGEX': '(?i)puff(s)?'}}]},
        {'label': 'MILLILITER', 'pattern': [
            {'TEXT': {'FUZZY': {'IN': ['ml', 'milliliter']}}}]}
    ]
    ruler.add_patterns(administration_forms)

    doc = nlp("2 millaleters twice a day")
    matches = matcher(doc)

    for ent in doc.ents:
        # all administration forms here
        if ent.label_ in ['TABLET', 'CAPLET', 'CAPSULE', 'PUFF', 'MILLILITER']:
            print(f"Entity: {ent.text}, Label: {ent.label_}")

    for match_id, start, end in matches:
        matched_span = doc[start:end]
        name = nlp.vocab.strings[match_id]
        # print(matched_span.text)
        # print(name)
        if name == 'DAILY_FREQUENCIES':
            print(f'Daily frequency: {matched_span.text}')
        if name == "DOSE_ADMINFORM":
            dose_matches = matcher(matched_span)
            for match_id, start, end in dose_matches:
                p_name = nlp.vocab.strings[match_id]
                if p_name == "DOSE":
                    # found dose here
                    print(f"Dose: {matched_span[start:end].text}")


if __name__ == "__main__":
    main()
