from common import pairwise
from unicode2ascii import read_u2a_data, convert_u2a

def document_to_ascii(document):
    # traverse sentences, store sentence head (text before the
    # first token), then traverse tokens in pairs, storing the
    # tail of each token (space between the token and the next),
    # convert token text to ASCII using convert_u2a(), redo token
    # offsets, then redo the sentence text using the head, token
    # texts and tails, and finally redo the document text using
    # the sentences.

    read_u2a_data()

    document.unicode_text = document.text
    offset = 0
    for sentence in document.sentences:
        sentence.unicode_text = sentence.text
        sent_end = sentence.base_offset + len(sentence.text)
        ascii_base_offset = offset

        if sentence.tokens:
            t_start = sentence.tokens[0].start
            sent_head = document.text[sentence.base_offset:t_start]
        else:
            sent_head = sentence.text
        assert not sent_head or sent_head.isspace()

        offset += len(sent_head)

        for t, next_t in pairwise(sentence.tokens, include_last=True):
            t.unicode_text = t.text
            tail_end = next_t.start if next_t is not None else sent_end
            t.tail = document.text[t.end:tail_end]
            assert not t.tail or t.tail.isspace()
            t.text = convert_u2a(t.text)
            t.start, t.end = offset, offset + len(t.text)
            offset += len(t.text) + len(t.tail)

        sentence.base_offset = ascii_base_offset
        sentence.text = sent_head + ''.join([t.text + t.tail 
                                             for t in sentence.tokens])

        assert sentence.is_valid()

    document.text = ''.join(s.text for s in document.sentences)
    assert document.is_valid()
