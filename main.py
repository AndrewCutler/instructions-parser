import spacy
from spacy.matcher import Matcher
from spacy.pipeline import EntityRuler
# from spacy.tokens import Token


def main():
    nlp = spacy.load("en_core_web_sm")

    matcher = Matcher(nlp.vocab)

    admin_forms = ["tab", "tablet", "tablets", "cap", "capsule", "caplet"]

    patterns_2 = [
        [
            {"POS": "VERB", "OP": "?"},
            {"LIKE_NUM": True},
            {"LOWER": {"IN": admin_forms}},
        ]
    ]

    matcher.add("TESTING", patterns_2)

    dose_number = [[{"LIKE_NUM": True}]]
    matcher.add('DOSE', dose_number)

    # administration_forms = [
    #     [{'TEXT': {'REGEX': 'tab(let)(s)'}}],
    #     [{'TEXT': {'REGEX': 'cap(let)(s)'}}],
    #     [{'TEXT': {'REGEX': 'cap(sule)(s)'}}],
    #     [{'TEXT': {'REGEX': 'puff(s)'}}]
    # ]
    # matcher.add('ADMINISTRATION_FORM', administration_forms)

    daily_frequencies = [
        [{'LIKE_NUM': True, 'OP': '?'}, {
            'TEXT': {'REGEX': 'a|per|every'}}, {'LOWER': 'day'}],
        [{'LIKE_NUM': True, 'OP': '?'}, {'LEMMA': 'daily'}]
    ]
    matcher.add('DAILY_FREQUENCIES', daily_frequencies)

    ruler = nlp.add_pipe('entity_ruler', before='ner')

	# case-insensitive regex
    administration_forms = [
        {'label': 'TABLET', 'pattern': [{'TEXT': {'REGEX': '(?i)tab(let)?(s)?'}}]},
        {'label': 'CAPLET', 'pattern': [{'TEXT': {'REGEX': '(?i)caplet(s)?'}}]},
        {'label': 'CAPSULE', 'pattern': [{'TEXT': {'REGEX': '(?i)cap(sule)(s)?'}}]},
        {'label': 'PUFF', 'pattern': [{'TEXT': {'REGEX': '(?i)puff(s)?'}}]}
    ]
    ruler.add_patterns(administration_forms)

    doc = nlp("2 tAbs twice a day")
    matches = matcher(doc)

    for ent in doc.ents:
        print(f"Entity: {ent.text}, Label: {ent.label_}")

    for match_id, start, end in matches:
        matched_span = doc[start:end]
        name = nlp.vocab.strings[match_id]
        # print(matched_span.text)
        # print(name)
        if name == 'DAILY_FREQUENCIES':
            print(f'Daily frequency: {matched_span.text}')
        if name == "TESTING":
            dose_matches = matcher(matched_span)
            for match_id, start, end in dose_matches:
                p_name = nlp.vocab.strings[match_id]
                if p_name == "DOSE":
                    # found dose here
                    print(f"Dose: {matched_span[start:end].text}")


if __name__ == "__main__":
    main()


# need to parse:
# dose
# administration form
# route of administration
# frequency
# dispense type

# administration forms: tablet, capsule, caplet, drop, puff, spray, inhalations,
