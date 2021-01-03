from nlp_service import processDocuments, processDocumentPair

DEFAULT_SIMILARITY = 0.5

class DummyNlp:
    def __init__(self, similarity=DEFAULT_SIMILARITY):
        self.sim = similarity
        self.calls = 0

    def __call__(self, text):
        self.calls += 1
        return self

    def similarity(self, x):
        self.calls += 1
        return self.sim

    def calls(self):
        return self.calls


def test_process_document_pair_similarity_lower_then_one():
    nlp_mock = DummyNlp()
    result = DEFAULT_SIMILARITY
    assert processDocumentPair(nlp_mock, nlp_mock) == result

def test_process_document_pair_similarity_should_be_boosted_when_equals_one():
    nlp_mock = DummyNlp(similarity=1)
    result = 2
    assert processDocumentPair(nlp_mock, nlp_mock, boost=True) == result

def test_process_documents_should_return_empty_array_when_passed_one_or_zero_documents():
    assert processDocuments(DummyNlp(), [], fields=[{"name":"text"}]) == {"similarities": []}
    assert processDocuments(DummyNlp(), [{"text": "bla"}],fields=[{"name":"text"}]) == {"similarities": []}

def test_process_documents_should_return_single_element_array_when_passed_two_documents():
    doc1, doc2 = {"text": "bla"}, {"text": "bleee"}
    assert processDocuments(DummyNlp(), [doc1, doc2], fields=[{"name":"text"}]) == {"similarities": [{"similarities": {"text":DEFAULT_SIMILARITY}, "docs":[doc1,doc2]}]}

def test_process_documents_should_return_single_element_array_when_passed_two_documents_with_two_fields():
    doc1, doc2 = {"text": "bla", "comment":"comment1"}, {"text": "bleee", "comment":"comment2"}
    assert processDocuments(DummyNlp(), [doc1, doc2], fields=[{"name":"text"}, {"name":"comment"}]) == {"similarities": [{"similarities": {"text":DEFAULT_SIMILARITY, "comment": DEFAULT_SIMILARITY}, "docs":[doc1,doc2]}]}
