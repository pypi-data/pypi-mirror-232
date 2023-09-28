import nltk
import string
from fuzzywuzzy import fuzz
import warnings

warnings.filterwarnings("ignore")
# nltk.download('stopwords')

# Load the stopwords and create a set for faster lookup
stop_words = set(nltk.corpus.stopwords.words('english'))


class NamedEntityRecognizer:
    def calculate_similarity(self, truth_value, predicted_value):
        truth_words = truth_value.lower().split()
        predicted_words = predicted_value.lower().split()

        return max(
            fuzz.ratio(truth_word, predicted_word) for truth_word in truth_words for predicted_word in predicted_words)

    def named_entity_recognition(self, truth_dict, prediction_dict, fuzzy_threshold):
        correct_entities = 0
        missed_entities = 0
        false_positive_entities = 0

        for entity_type, truth_values in truth_dict.items():
            predicted_values = prediction_dict.get(entity_type, [])

            for truth_value in truth_values:
                found = any(
                    self.calculate_similarity(truth_value, predicted_value) >= fuzzy_threshold for predicted_value
                    in predicted_values)

                if not found:
                    missed_entities += 1

            for predicted_value in predicted_values:
                found = any(
                    self.calculate_similarity(truth_value, predicted_value) >= fuzzy_threshold for truth_value in
                    truth_values)

                if not found:
                    false_positive_entities += 1

            correct_entities += len(truth_values) - missed_entities

        results_dict = {
            "Correct Entities": correct_entities,
            "Missed Entities": missed_entities,
            "False Positive Entities": false_positive_entities
        }

        return results_dict


ner = NamedEntityRecognizer()
